"""
Cause List data model - represents daily cause lists from courts.
"""

import datetime as dt
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class CauseListStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ADJOURNED = "adjourned"


class CauseListEntry(BaseModel):
    """Single entry/item in a cause list."""
    serial_number: int
    case_number: str
    case_type: Optional[str] = None
    petitioner: str
    respondent: str
    advocate_petitioner: Optional[str] = None
    advocate_respondent: Optional[str] = None
    listing_date: dt.date
    court_number: Optional[str] = None
    bench: Optional[str] = None
    item_number: Optional[int] = None
    remarks: Optional[str] = None
    status: CauseListStatus = CauseListStatus.SCHEDULED
    hearing_time: Optional[str] = None


class CauseList(BaseModel):
    """Complete cause list for a court on a specific date."""
    court_name: str = Field(..., description="Name of the court")
    court_type: str = Field(default="high_court")
    list_date: dt.date = Field(..., description="Date of the cause list")
    bench: Optional[str] = None
    court_number: Optional[str] = None
    judge_name: Optional[str] = None
    total_cases: int = 0
    entries: List[CauseListEntry] = []
    pdf_url: Optional[str] = None
    source_url: Optional[str] = None
    scraped_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "court_name": "Delhi High Court",
                "court_type": "high_court",
                "list_date": "2024-01-15",
                "total_cases": 42,
                "entries": [],
            }
        }
    }


class CauseListFilter(BaseModel):
    """Filter parameters for cause list queries."""
    court_name: Optional[str] = None
    court_type: Optional[str] = None
    date_from: Optional[dt.date] = None
    date_to: Optional[dt.date] = None
    bench: Optional[str] = None
    judge_name: Optional[str] = None
    case_number: Optional[str] = None
    advocate: Optional[str] = None
    page: int = 1
    limit: int = 20


class CauseListResponse(BaseModel):
    """API response for single cause list."""
    success: bool = True
    data: Optional[CauseList] = None
    message: str = ""


class CauseListListResponse(BaseModel):
    """API response for multiple cause lists."""
    success: bool = True
    data: List[CauseList] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    message: str = ""


class MonitoredCase(BaseModel):
    """Case being monitored for cause list appearances."""
    case_number: str
    court_name: str
    user_id: str
    notify_email: Optional[str] = None
    notify_phone: Optional[str] = None
    is_active: bool = True
    last_seen_date: Optional[dt.date] = None
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
