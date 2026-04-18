"""
Case data model - represents court cases and related entities.
"""

import datetime as dt
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class CaseStatus(str, Enum):
    PENDING = "pending"
    LISTED = "listed"
    HEARD = "heard"
    DISPOSED = "disposed"
    ADJOURNED = "adjourned"
    RESERVED = "reserved"


class CourtType(str, Enum):
    SUPREME_COURT = "supreme_court"
    HIGH_COURT = "high_court"
    DISTRICT_COURT = "district_court"
    TRIBUNAL = "tribunal"
    CONSUMER_FORUM = "consumer_forum"


class CaseType(str, Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    WRIT = "writ"
    APPEAL = "appeal"
    REVISION = "revision"
    MISC = "miscellaneous"


class HearingRecord(BaseModel):
    """Individual hearing record within a case."""
    hearing_date: dt.date
    court_number: Optional[str] = None
    judge: Optional[str] = None
    order_summary: Optional[str] = None
    next_hearing: Optional[dt.date] = None
    status: CaseStatus = CaseStatus.PENDING


class Case(BaseModel):
    """Full case representation."""
    case_number: str = Field(..., description="Court case number e.g. WP(C)/1234/2024")
    case_type: CaseType = CaseType.CIVIL
    court_type: CourtType = CourtType.HIGH_COURT
    court_name: str = Field(..., description="Name of the court")
    petitioner: str = Field(..., description="Petitioner/plaintiff name")
    respondent: str = Field(..., description="Respondent/defendant name")
    advocate_petitioner: Optional[str] = None
    advocate_respondent: Optional[str] = None
    filing_date: Optional[dt.date] = None
    next_hearing_date: Optional[dt.date] = None
    status: CaseStatus = CaseStatus.PENDING
    subject: Optional[str] = None
    act: Optional[str] = None
    section: Optional[str] = None
    bench: Optional[str] = None
    hearings: List[HearingRecord] = []
    scraped_at: Optional[dt.datetime] = None
    created_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    updated_at: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "case_number": "WP(C)/1234/2024",
                "case_type": "writ",
                "court_type": "high_court",
                "court_name": "Delhi High Court",
                "petitioner": "Ram Kumar",
                "respondent": "State of Delhi",
                "status": "pending",
            }
        }
    )


class CaseCreate(BaseModel):
    """Schema for creating a new case."""
    case_number: str
    case_type: CaseType = CaseType.CIVIL
    court_type: CourtType = CourtType.HIGH_COURT
    court_name: str
    petitioner: str
    respondent: str
    advocate_petitioner: Optional[str] = None
    advocate_respondent: Optional[str] = None
    filing_date: Optional[dt.date] = None
    subject: Optional[str] = None


class CaseUpdate(BaseModel):
    """Schema for updating a case."""
    status: Optional[CaseStatus] = None
    next_hearing_date: Optional[dt.date] = None
    advocate_petitioner: Optional[str] = None
    advocate_respondent: Optional[str] = None
    bench: Optional[str] = None
    subject: Optional[str] = None


class CaseSearchQuery(BaseModel):
    """Search query parameters for case lookup."""
    case_number: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    advocate: Optional[str] = None
    court_type: Optional[CourtType] = None
    court_name: Optional[str] = None
    case_type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None
    date_from: Optional[dt.date] = None
    date_to: Optional[dt.date] = None
    page: int = 1
    limit: int = 20


class CaseResponse(BaseModel):
    """API response wrapper for case data."""
    success: bool = True
    data: Optional[Case] = None
    message: str = ""


class CaseListResponse(BaseModel):
    """API response wrapper for multiple cases."""
    success: bool = True
    data: List[Case] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    message: str = ""
