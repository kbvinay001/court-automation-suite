"""
Scraper Service - Business logic for court data scraping operations.
"""

from datetime import date, timedelta
from typing import Optional, List, Dict, Any, Tuple
import logging

from api.models.case import Case, CaseSearchQuery, CaseStatus, CourtType
from api.models.causelist import CauseList, CauseListFilter, MonitoredCase
from utils.database import (
    find_one, find_many, insert_one, update_one,
    count_documents, delete_one, aggregate,
)

logger = logging.getLogger(__name__)


class ScraperService:
    """Business logic layer for scraping and case management."""

    # ─────────────────── CASE OPERATIONS ───────────────────

    async def search_cases(self, query: CaseSearchQuery) -> Tuple[List[Case], int]:
        """Search cases with filters and pagination."""
        mongo_query: Dict[str, Any] = {}

        if query.case_number:
            mongo_query["case_number"] = {"$regex": query.case_number, "$options": "i"}
        if query.petitioner:
            mongo_query["petitioner"] = {"$regex": query.petitioner, "$options": "i"}
        if query.respondent:
            mongo_query["respondent"] = {"$regex": query.respondent, "$options": "i"}
        if query.advocate:
            mongo_query["$or"] = [
                {"advocate_petitioner": {"$regex": query.advocate, "$options": "i"}},
                {"advocate_respondent": {"$regex": query.advocate, "$options": "i"}},
            ]
        if query.court_type:
            mongo_query["court_type"] = query.court_type.value
        if query.court_name:
            mongo_query["court_name"] = query.court_name
        if query.case_type:
            mongo_query["case_type"] = query.case_type.value
        if query.status:
            mongo_query["status"] = query.status.value
        if query.date_from:
            mongo_query.setdefault("next_hearing_date", {})["$gte"] = query.date_from.isoformat()
        if query.date_to:
            mongo_query.setdefault("next_hearing_date", {})["$lte"] = query.date_to.isoformat()

        skip = (query.page - 1) * query.limit
        total = await count_documents("cases", mongo_query)
        docs = await find_many(
            "cases", mongo_query,
            skip=skip, limit=query.limit,
            sort=[("updated_at", -1)],
        )
        cases = [Case(**doc) for doc in docs]
        return cases, total

    async def get_case(self, case_number: str) -> Optional[Case]:
        """Get a single case by case number."""
        doc = await find_one("cases", {"case_number": case_number.upper()})
        return Case(**doc) if doc else None

    async def scrape_case(
        self, case_number: str, court_type: CourtType, court_name: str
    ) -> Optional[Case]:
        """Scrape a case from court website and store it."""
        from scrapers import get_scraper

        scraper = get_scraper(court_type, court_name)
        if not scraper:
            logger.error(f"No scraper available for {court_type} - {court_name}")
            return None

        try:
            case_data = await scraper.scrape_case(case_number)
            if not case_data:
                return None

            # Upsert in database
            existing = await find_one("cases", {"case_number": case_number.upper()})
            if existing:
                await update_one(
                    "cases",
                    {"case_number": case_number.upper()},
                    case_data,
                )
            else:
                await insert_one("cases", case_data)

            return Case(**case_data)
        except Exception as e:
            logger.error(f"Scraping failed for {case_number}: {e}")
            raise

    async def batch_scrape(
        self, case_numbers: List[str], court_type: CourtType, court_name: str
    ):
        """Scrape multiple cases (used as background task)."""
        results = {"success": [], "failed": []}
        for cn in case_numbers:
            try:
                case = await self.scrape_case(cn, court_type, court_name)  # type: ignore[misc]
                if case:
                    results["success"].append(cn)
                else:
                    results["failed"].append(cn)
            except Exception:
                results["failed"].append(cn)
        logger.info(
            f"Batch scrape complete: {len(results['success'])} success, "
            f"{len(results['failed'])} failed"
        )
        return results

    # ─────────────────── TRACKING ───────────────────

    async def track_case(
        self, case_number: str, user_id: str,
        notify_email: Optional[str] = None, notify_phone: Optional[str] = None,
    ) -> dict:
        """Track a case for a user."""
        tracking = {
            "case_number": case_number.upper(),
            "user_id": user_id,
            "notify_email": notify_email,
            "notify_phone": notify_phone,
            "is_active": True,
        }

        existing = await find_one("tracked_cases", {
            "case_number": case_number.upper(),
            "user_id": user_id,
        })
        if existing:
            await update_one(
                "tracked_cases",
                {"case_number": case_number.upper(), "user_id": user_id},
                {"is_active": True, "notify_email": notify_email, "notify_phone": notify_phone},
            )
        else:
            await insert_one("tracked_cases", tracking)

        return tracking

    async def untrack_case(self, case_number: str, user_id: str):
        """Stop tracking a case."""
        await update_one(
            "tracked_cases",
            {"case_number": case_number.upper(), "user_id": user_id},
            {"is_active": False},
        )

    async def get_tracked_cases(
        self, user_id: str, page: int = 1, limit: int = 20
    ) -> Tuple[List[Case], int]:
        """Get all tracked cases for a user."""
        tracked = await find_many(
            "tracked_cases",
            {"user_id": user_id, "is_active": True},
        )
        case_numbers = [t["case_number"] for t in tracked]
        if not case_numbers:
            return [], 0

        query = {"case_number": {"$in": case_numbers}}
        total = await count_documents("cases", query)
        skip = (page - 1) * limit
        docs = await find_many("cases", query, skip=skip, limit=limit)
        return [Case(**doc) for doc in docs], total

    async def get_upcoming_hearings(
        self, user_id: Optional[str] = None, days: int = 7,
        page: int = 1, limit: int = 20,
    ) -> Tuple[List[Case], int]:
        """Get upcoming hearings."""
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=days)).isoformat()

        query: Dict[str, Any] = {
            "next_hearing_date": {"$gte": today, "$lte": end_date},
        }

        if user_id:
            tracked = await find_many(
                "tracked_cases",
                {"user_id": user_id, "is_active": True},
            )
            case_numbers = [t["case_number"] for t in tracked]
            if case_numbers:
                query["case_number"] = {"$in": case_numbers}

        total = await count_documents("cases", query)
        skip = (page - 1) * limit
        docs = await find_many(
            "cases", query,
            skip=skip, limit=limit,
            sort=[("next_hearing_date", 1)],
        )
        return [Case(**doc) for doc in docs], total

    # ─────────────────── CAUSE LIST OPERATIONS ───────────────────

    async def get_cause_list(
        self, court_name: str, target_date: date,
        bench: Optional[str] = None, court_number: Optional[str] = None,
    ) -> List[CauseList]:
        """Get cause lists for a court on a specific date."""
        query: Dict[str, Any] = {
            "court_name": court_name,
            "date": target_date.isoformat(),
        }
        if bench:
            query["bench"] = bench
        if court_number:
            query["court_number"] = court_number

        docs = await find_many("causelists", query)
        if docs:
            return [CauseList(**doc) for doc in docs]

        # If no data, try scraping
        return await self.refresh_cause_list(court_name, target_date)

    async def refresh_cause_list(self, court_name: str, target_date: date) -> List[CauseList]:
        """Re-scrape cause list from court website."""
        from scrapers.causelist_scraper import CauseListScraper

        scraper = CauseListScraper()
        try:
            cause_lists = await scraper.scrape_causelist(court_name, target_date)
            for cl in cause_lists:
                data = cl.model_dump(mode="json")
                existing = await find_one("causelists", {
                    "court_name": court_name,
                    "date": target_date.isoformat(),
                    "court_number": data.get("court_number"),
                })
                if existing:
                    await update_one(
                        "causelists",
                        {"_id": existing["_id"]},
                        data,
                    )
                else:
                    await insert_one("causelists", data)
            return cause_lists
        except Exception as e:
            logger.error(f"Cause list refresh failed: {e}")
            return []

    async def search_cause_lists(
        self, filters: CauseListFilter, party_name: Optional[str] = None
    ) -> Tuple[List[CauseList], int]:
        """Search cause lists with filters."""
        query: Dict[str, Any] = {}
        if filters.court_name:
            query["court_name"] = filters.court_name
        if filters.date_from:
            query.setdefault("date", {})["$gte"] = filters.date_from.isoformat()
        if filters.date_to:
            query.setdefault("date", {})["$lte"] = filters.date_to.isoformat()
        if filters.bench:
            query["bench"] = filters.bench
        if filters.case_number:
            query["entries.case_number"] = {"$regex": filters.case_number, "$options": "i"}
        if filters.advocate:
            query["$or"] = [
                {"entries.advocate_petitioner": {"$regex": filters.advocate, "$options": "i"}},
                {"entries.advocate_respondent": {"$regex": filters.advocate, "$options": "i"}},
            ]
        if party_name:
            query.setdefault("$or", []).extend([
                {"entries.petitioner": {"$regex": party_name, "$options": "i"}},
                {"entries.respondent": {"$regex": party_name, "$options": "i"}},
            ])

        skip = (filters.page - 1) * filters.limit
        total = await count_documents("causelists", query)
        docs = await find_many("causelists", query, skip=skip, limit=filters.limit)
        return [CauseList(**doc) for doc in docs], total

    # ─────────────────── MONITORS ───────────────────

    async def add_causelist_monitor(self, monitor: MonitoredCase) -> dict:
        """Add cause list monitor."""
        data = monitor.model_dump(mode="json")
        existing = await find_one("monitored_cases", {
            "case_number": monitor.case_number,
            "user_id": monitor.user_id,
        })
        if existing:
            await update_one(
                "monitored_cases",
                {"case_number": monitor.case_number, "user_id": monitor.user_id},
                {"is_active": True},
            )
        else:
            await insert_one("monitored_cases", data)
        return data

    async def remove_causelist_monitor(self, case_number: str, user_id: str):
        """Remove cause list monitor."""
        await update_one(
            "monitored_cases",
            {"case_number": case_number, "user_id": user_id},
            {"is_active": False},
        )

    async def get_user_monitors(self, user_id: str) -> List[dict]:
        """Get all monitors for a user."""
        return await find_many(
            "monitored_cases",
            {"user_id": user_id, "is_active": True},
        )
