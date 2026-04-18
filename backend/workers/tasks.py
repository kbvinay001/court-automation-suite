"""
Celery Tasks - Background task definitions for court automation.
"""

import logging
from datetime import date, timedelta
from typing import List

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


# ─────────────────── SCRAPING TASKS ───────────────────

@celery_app.task(bind=True, name="workers.tasks.scrape_case")
def scrape_case(self, case_number: str, court_type: str, court_name: str):
    """Scrape a single case from court website."""
    import asyncio
    from api.services.scraper_service import ScraperService

    async def _scrape():
        service = ScraperService()
        result = await service.scrape_case(case_number, court_type, court_name)
        return result.model_dump(mode="json") if result else None

    try:
        result = asyncio.get_event_loop().run_until_complete(_scrape())
        logger.info(f"Scraped case {case_number}: {'success' if result else 'not found'}")
        return result
    except Exception as e:
        logger.error(f"Task scrape_case failed for {case_number}: {e}")
        raise self.retry(exc=e)


@celery_app.task(bind=True, name="workers.tasks.batch_scrape_cases")
def batch_scrape_cases(
    self, case_numbers: List[str], court_type: str, court_name: str
):
    """Scrape multiple cases in batch."""
    import asyncio
    from api.services.scraper_service import ScraperService

    async def _batch():
        service = ScraperService()
        return await service.batch_scrape(case_numbers, court_type, court_name)

    try:
        results = asyncio.get_event_loop().run_until_complete(_batch())
        logger.info(
            f"Batch scrape complete: {len(results.get('success', []))} success, "  # type: ignore[union-attr]
            f"{len(results.get('failed', []))} failed"  # type: ignore[union-attr]
        )
        return results
    except Exception as e:
        logger.error(f"Batch scrape failed: {e}")
        raise self.retry(exc=e)


@celery_app.task(name="workers.tasks.scrape_daily_causelists")
def scrape_daily_causelists():
    """Scrape today's cause lists from all configured courts."""
    import asyncio
    from scrapers.causelist_scraper import CauseListScraper

    courts = [
        "Delhi High Court", "Bombay High Court", "Madras High Court",
        "Calcutta High Court", "Karnataka High Court", "Allahabad High Court",
        "Supreme Court of India",
    ]

    async def _scrape_all():
        scraper = CauseListScraper()
        today = date.today()
        total_entries = 0

        for court in courts:
            try:
                cause_lists = await scraper.scrape_causelist(court, today)
                entries = sum(cl.total_cases for cl in cause_lists)
                total_entries += entries  # type: ignore[operator]
                logger.info(f"Scraped {court}: {entries} entries")
            except Exception as e:
                logger.error(f"Failed to scrape {court}: {e}")

        return total_entries

    try:
        total = asyncio.get_event_loop().run_until_complete(_scrape_all())
        logger.info(f"Daily cause list scrape complete: {total} total entries")
        return {"total_entries": total, "courts_scraped": len(courts)}
    except Exception as e:
        logger.error(f"Daily cause list scrape failed: {e}")
        return {"error": str(e)}


# ─────────────────── NOTIFICATION TASKS ───────────────────

@celery_app.task(name="workers.tasks.check_tracked_case_updates")
def check_tracked_case_updates():
    """Check all tracked cases for updates and notify users."""
    import asyncio
    from utils.database import find_many, find_one
    from api.services.notification_service import NotificationService

    async def _check():
        # Get all active tracked cases
        tracked = await find_many("tracked_cases", {"is_active": True}, limit=500)
        notification_service = NotificationService()
        notifications_sent = 0

        for track in tracked:
            case_number = track["case_number"]
            # Check if case appears in today's cause list
            today_str = date.today().isoformat()
            causelist_entry = await find_one("causelists", {
                "date": today_str,
                "entries.case_number": {"$regex": case_number, "$options": "i"},
            })

            if causelist_entry:
                # Case is listed today - notify
                case = await find_one("cases", {"case_number": case_number})
                if case:
                    recipients = [track]
                    await notification_service.notify_case_listed(case, recipients)
                    notifications_sent += 1  # type: ignore[operator]

        return notifications_sent

    try:
        count = asyncio.get_event_loop().run_until_complete(_check())
        logger.info(f"Tracked case check complete: {count} notifications sent")
        return {"notifications_sent": count}
    except Exception as e:
        logger.error(f"Tracked case check failed: {e}")
        return {"error": str(e)}


@celery_app.task(name="workers.tasks.send_hearing_reminders")
def send_hearing_reminders():
    """Send reminders for hearings scheduled today and tomorrow."""
    import asyncio
    from utils.database import find_many
    from api.services.notification_service import NotificationService

    async def _send_reminders():
        notification_service = NotificationService()
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        # Find cases with hearings today or tomorrow
        cases = await find_many("cases", {
            "next_hearing_date": {"$in": [today, tomorrow]},
        }, limit=200)

        reminders_sent = 0
        for case in cases:
            case_number = case["case_number"]
            # Find users tracking this case
            trackers = await find_many("tracked_cases", {
                "case_number": case_number,
                "is_active": True,
            })

            if trackers:
                await notification_service.notify_hearing_reminder(case, trackers)
                reminders_sent += 1  # type: ignore[operator]

        return reminders_sent

    try:
        count = asyncio.get_event_loop().run_until_complete(_send_reminders())
        logger.info(f"Hearing reminders sent: {count}")
        return {"reminders_sent": count}
    except Exception as e:
        logger.error(f"Hearing reminders failed: {e}")
        return {"error": str(e)}


@celery_app.task(name="workers.tasks.send_daily_digest")
def send_daily_digest():
    """Send daily digest to all subscribed users."""
    import asyncio
    from utils.database import find_many
    from api.services.notification_service import NotificationService

    async def _send_digests():
        notification_service = NotificationService()

        # Get users with daily digest enabled
        users = await find_many("users", {
            "notification_preferences.daily_digest": True,
            "is_active": True,
        }, limit=500)

        digests_sent = 0
        for user in users:
            # Get user's tracked cases
            tracked = await find_many("tracked_cases", {
                "user_id": str(user.get("_id", "")),
                "is_active": True,
            })

            case_numbers = [t["case_number"] for t in tracked]
            if not case_numbers:
                continue

            # Get case details
            cases = await find_many("cases", {
                "case_number": {"$in": case_numbers},
            })

            if cases:
                digest = {"cases": cases, "date": date.today().isoformat()}
                await notification_service.send_daily_digest(user, digest)
                digests_sent += 1  # type: ignore[operator]

        return digests_sent

    try:
        count = asyncio.get_event_loop().run_until_complete(_send_digests())
        logger.info(f"Daily digests sent: {count}")
        return {"digests_sent": count}
    except Exception as e:
        logger.error(f"Daily digest failed: {e}")
        return {"error": str(e)}


# ─────────────────── MAINTENANCE TASKS ───────────────────

@celery_app.task(name="workers.tasks.cleanup_old_data")
def cleanup_old_data():
    """Clean up old cause lists and cache entries."""
    import asyncio
    from utils.database import get_db
    from utils.cache import cache_clear_pattern

    async def _cleanup():
        db = get_db()
        if not db:
            return {"error": "Database not available"}

        # Delete cause lists older than 90 days
        cutoff = (date.today() - timedelta(days=90)).isoformat()
        result = await db.causelists.delete_many({"date": {"$lt": cutoff}})
        deleted_causelists = result.deleted_count

        # Clear expired cache entries
        cleared = await cache_clear_pattern("court:*")

        return {
            "deleted_causelists": deleted_causelists,
            "cache_entries_cleared": cleared,
        }

    try:
        result = asyncio.get_event_loop().run_until_complete(_cleanup())
        logger.info(f"Cleanup complete: {result}")
        return result
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"error": str(e)}


@celery_app.task(name="workers.tasks.generate_pdf_report")
def generate_pdf_report(report_type: str, data: dict):
    """Generate a PDF report asynchronously."""
    from api.services.pdf_generator import PDFGenerator

    generator = PDFGenerator()
    try:
        if report_type == "causelist":
            filepath = generator.generate_cause_list_pdf(
                data, data.get("court_name", ""), date.fromisoformat(data.get("date", ""))
            )
        elif report_type == "case":
            filepath = generator.generate_case_report_pdf(data)
        elif report_type == "analytics":
            filepath = generator.generate_analytics_report_pdf(data)
        else:
            return {"error": f"Unknown report type: {report_type}"}

        return {"filepath": filepath, "success": True}
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return {"error": str(e)}
