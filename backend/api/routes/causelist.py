"""
Cause List API routes - endpoints for cause list monitoring and search.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, timedelta

from api.models.causelist import (
    CauseList, CauseListEntry, CauseListFilter,
    CauseListResponse, CauseListListResponse, MonitoredCase,
)
from api.services.scraper_service import ScraperService
from utils.cache import cache_get, cache_set, get_cached_causelist, cache_causelist

router = APIRouter()
scraper_service = ScraperService()


@router.get("/today", response_model=CauseListListResponse)
async def get_today_causelist(
    court_name: str = Query(..., description="Court name"),
    bench: Optional[str] = Query(None, description="Bench/division"),
    court_number: Optional[str] = Query(None, description="Specific court number"),
):
    """Get today's cause list for a specific court."""
    today = date.today()
    return await _get_causelist_for_date(today, court_name, bench, court_number)


@router.get("/date/{target_date}", response_model=CauseListListResponse)
async def get_causelist_by_date(
    target_date: date,
    court_name: str = Query(..., description="Court name"),
    bench: Optional[str] = Query(None, description="Bench/division"),
    court_number: Optional[str] = Query(None, description="Specific court number"),
):
    """Get cause list for a specific date."""
    return await _get_causelist_for_date(target_date, court_name, bench, court_number)


async def _get_causelist_for_date(
    target_date: date, court_name: str,
    bench: Optional[str], court_number: Optional[str],
) -> CauseListListResponse:
    """Internal helper to get cause list for a date."""
    cache_key = f"causelist:{court_name}:{target_date.isoformat()}"
    if bench:
        cache_key += f":{bench}"

    # Check cache
    cached = await cache_get(cache_key)
    if cached:
        cause_lists = [CauseList(**cl) for cl in cached]
        return CauseListListResponse(
            data=cause_lists, total=len(cause_lists), message="From cache"
        )

    try:
        cause_lists = await scraper_service.get_cause_list(
            court_name=court_name, target_date=target_date,
            bench=bench, court_number=court_number,
        )

        # Cache for 15 minutes
        await cache_set(
            cache_key,
            [cl.model_dump(mode="json") for cl in cause_lists],
            ttl=900,
        )

        return CauseListListResponse(data=cause_lists, total=len(cause_lists))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cause list: {str(e)}")


@router.get("/search", response_model=CauseListListResponse)
async def search_causelist(
    case_number: Optional[str] = Query(None, description="Search by case number"),
    advocate: Optional[str] = Query(None, description="Search by advocate name"),
    party_name: Optional[str] = Query(None, description="Search by party name"),
    court_name: Optional[str] = Query(None, description="Court name"),
    date_from: Optional[date] = Query(None, description="Start date"),
    date_to: Optional[date] = Query(None, description="End date"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Search cause lists across dates and courts."""
    filters = CauseListFilter(
        court_name=court_name,
        date_from=date_from or date.today(),
        date_to=date_to or (date.today() + timedelta(days=7)),
        case_number=case_number,
        advocate=advocate,
        page=page,
        limit=limit,
    )

    try:
        cause_lists, total = await scraper_service.search_cause_lists(filters, party_name)
        return CauseListListResponse(
            data=cause_lists, total=total, page=page, limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/monitor")
async def add_case_monitor(
    case_number: str = Query(..., description="Case number to monitor"),
    court_name: str = Query(..., description="Court name"),
    user_id: str = Query(..., description="User ID"),
    notify_email: Optional[str] = Query(None),
    notify_phone: Optional[str] = Query(None),
):
    """Add a case to cause list monitoring."""
    try:
        monitor = MonitoredCase(
            case_number=case_number,
            court_name=court_name,
            user_id=user_id,
            notify_email=notify_email,
            notify_phone=notify_phone,
        )
        result = await scraper_service.add_causelist_monitor(monitor)
        return {"success": True, "message": f"Monitoring {case_number}", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/monitor/{case_number}")
async def remove_case_monitor(
    case_number: str,
    user_id: str = Query(..., description="User ID"),
):
    """Remove a case from cause list monitoring."""
    try:
        await scraper_service.remove_causelist_monitor(case_number, user_id)
        return {"success": True, "message": f"Stopped monitoring {case_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitors")
async def get_monitored_cases(
    user_id: str = Query(..., description="User ID"),
):
    """Get all cases being monitored by a user."""
    try:
        monitors = await scraper_service.get_user_monitors(user_id)
        return {"success": True, "data": monitors, "total": len(monitors)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_causelist(
    court_name: str = Query(..., description="Court name"),
    target_date: Optional[date] = Query(None, description="Date (default: today)"),
):
    """Force refresh cause list by re-scraping from court website."""
    target = target_date or date.today()

    try:
        cause_lists = await scraper_service.refresh_cause_list(court_name, target)
        return {
            "success": True,
            "message": f"Refreshed {len(cause_lists)} cause lists for {court_name}",
            "total_entries": sum(cl.total_cases for cl in cause_lists),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")


@router.get("/courts")
async def get_courts_with_causelists():
    """Get list of courts that provide digital cause lists."""
    return {
        "success": True,
        "data": [
            {"name": "Delhi High Court", "url": "https://delhihighcourt.nic.in", "digital_causelist": True},
            {"name": "Bombay High Court", "url": "https://bombayhighcourt.nic.in", "digital_causelist": True},
            {"name": "Madras High Court", "url": "https://www.mhc.tn.gov.in", "digital_causelist": True},
            {"name": "Calcutta High Court", "url": "https://calcuttahighcourt.gov.in", "digital_causelist": True},
            {"name": "Karnataka High Court", "url": "https://karnatakajudiciary.kar.nic.in", "digital_causelist": True},
            {"name": "Allahabad High Court", "url": "https://www.allahabadhighcourt.in", "digital_causelist": True},
            {"name": "Supreme Court of India", "url": "https://www.sci.gov.in", "digital_causelist": True},
        ],
    }


@router.get("/week")
async def get_week_causelist(
    court_name: str = Query(..., description="Court name"),
    start_date: Optional[date] = Query(None, description="Start date (default: Monday of current week)"),
):
    """Get cause lists for the entire week."""
    if not start_date:
        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # Monday

    try:
        weekly_data = {}
        for i in range(5):  # Monday to Friday
            day = start_date + timedelta(days=i)
            day_str = day.isoformat()
            cause_lists = await scraper_service.get_cause_list(
                court_name=court_name, target_date=day
            )
            weekly_data[day_str] = {
                "date": day_str,
                "day": day.strftime("%A"),
                "total_cases": sum(cl.total_cases for cl in cause_lists),
                "cause_lists": [cl.model_dump(mode="json") for cl in cause_lists],
            }

        return {"success": True, "court": court_name, "week_data": weekly_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
