"""
Court Scraper API routes - endpoints for case search, scraping, and tracking.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List
from datetime import date

from api.models.case import (
    Case, CaseCreate, CaseUpdate, CaseResponse, CaseListResponse,
    CaseSearchQuery, CaseStatus, CourtType, CaseType,
)
from api.services.scraper_service import ScraperService
from utils.validators import validate_case_number, sanitize_input
from utils.cache import cache_get, cache_set, get_cached_case, cache_case

router = APIRouter()
scraper_service = ScraperService()


@router.get("/search", response_model=CaseListResponse)
async def search_cases(
    case_number: Optional[str] = Query(None, description="Case number to search"),
    petitioner: Optional[str] = Query(None, description="Petitioner name"),
    respondent: Optional[str] = Query(None, description="Respondent name"),
    advocate: Optional[str] = Query(None, description="Advocate name"),
    court_type: Optional[CourtType] = Query(None, description="Type of court"),
    court_name: Optional[str] = Query(None, description="Court name"),
    case_type: Optional[CaseType] = Query(None, description="Type of case"),
    status: Optional[CaseStatus] = Query(None, description="Case status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
):
    """Search for court cases with various filters."""
    query = CaseSearchQuery(
        case_number=sanitize_input(case_number) if case_number else None,
        petitioner=sanitize_input(petitioner) if petitioner else None,
        respondent=sanitize_input(respondent) if respondent else None,
        advocate=sanitize_input(advocate) if advocate else None,
        court_type=court_type,
        court_name=court_name,
        case_type=case_type,
        status=status,
        page=page,
        limit=limit,
    )

    try:
        cases, total = await scraper_service.search_cases(query)
        return CaseListResponse(data=cases, total=total, page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/case/{case_number}", response_model=CaseResponse)
async def get_case_details(case_number: str):
    """Get detailed information about a specific case."""
    if not validate_case_number(case_number):
        raise HTTPException(status_code=400, detail="Invalid case number format")

    # Check cache first
    cached = await get_cached_case(case_number)
    if cached:
        return CaseResponse(data=Case(**cached), message="From cache")

    try:
        case = await scraper_service.get_case(case_number)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Cache the result
        await cache_case(case_number, case.model_dump(mode="json"))
        return CaseResponse(data=case)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch case: {str(e)}")


@router.post("/scrape", response_model=CaseResponse)
async def scrape_case(
    case_number: str = Query(..., description="Case number to scrape"),
    court_type: CourtType = Query(CourtType.HIGH_COURT, description="Court type"),
    court_name: str = Query(..., description="Court name"),
    background_tasks: BackgroundTasks = None,
):
    """Scrape a specific case from court website."""
    if not validate_case_number(case_number):
        raise HTTPException(status_code=400, detail="Invalid case number format")

    try:
        case = await scraper_service.scrape_case(case_number, court_type, court_name)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found on court website")
        return CaseResponse(data=case, message="Case scraped successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.post("/scrape/batch")
async def batch_scrape(
    case_numbers: List[str],
    court_type: CourtType = Query(CourtType.HIGH_COURT),
    court_name: str = Query(...),
    background_tasks: BackgroundTasks = None,
):
    """Queue multiple cases for background scraping."""
    if len(case_numbers) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 cases per batch")

    valid_cases = [cn for cn in case_numbers if validate_case_number(cn)]
    invalid_cases = [cn for cn in case_numbers if not validate_case_number(cn)]

    if background_tasks:
        background_tasks.add_task(
            scraper_service.batch_scrape, valid_cases, court_type, court_name
        )

    return {
        "success": True,
        "message": f"Queued {len(valid_cases)} cases for scraping",
        "queued": len(valid_cases),
        "invalid": invalid_cases,
    }


@router.post("/track/{case_number}")
async def track_case(
    case_number: str,
    user_id: str = Query(..., description="User ID"),
    notify_email: Optional[str] = Query(None),
    notify_phone: Optional[str] = Query(None),
):
    """Start tracking a case for updates."""
    if not validate_case_number(case_number):
        raise HTTPException(status_code=400, detail="Invalid case number format")

    try:
        result = await scraper_service.track_case(
            case_number, user_id, notify_email, notify_phone
        )
        return {"success": True, "message": f"Now tracking case {case_number}", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/track/{case_number}")
async def untrack_case(
    case_number: str,
    user_id: str = Query(..., description="User ID"),
):
    """Stop tracking a case."""
    try:
        await scraper_service.untrack_case(case_number, user_id)
        return {"success": True, "message": f"Stopped tracking case {case_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracked")
async def get_tracked_cases(
    user_id: str = Query(..., description="User ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get all cases tracked by a user."""
    try:
        cases, total = await scraper_service.get_tracked_cases(user_id, page, limit)
        return CaseListResponse(data=cases, total=total, page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/upcoming")
async def upcoming_hearings(
    user_id: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30, description="Days ahead to look"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get upcoming hearings for tracked cases."""
    try:
        hearings, total = await scraper_service.get_upcoming_hearings(
            user_id=user_id, days=days, page=page, limit=limit
        )
        return CaseListResponse(data=hearings, total=total, page=page, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/courts")
async def list_supported_courts():
    """List all supported courts for scraping."""
    return {
        "success": True,
        "data": {
            "high_courts": [
                "Delhi High Court", "Bombay High Court", "Madras High Court",
                "Calcutta High Court", "Karnataka High Court", "Allahabad High Court",
                "Andhra Pradesh High Court", "Telangana High Court", "Kerala High Court",
                "Punjab and Haryana High Court", "Rajasthan High Court",
                "Gujarat High Court", "Orissa High Court", "Patna High Court",
            ],
            "supreme_court": ["Supreme Court of India"],
            "tribunals": ["NCLAT", "NCDRC", "NGT", "ITAT", "SAT"],
        },
    }
