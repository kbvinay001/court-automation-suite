"""
Validators utility - Input validation helpers for court data.
"""

import re
from datetime import date, datetime
from typing import Optional


def validate_case_number(case_number: str) -> bool:
    """
    Validate Indian court case number formats.
    Supports: WP(C)/1234/2024, CRL.A./567/2023, CS(OS)/89/2022, etc.
    """
    if not case_number or not isinstance(case_number, str):
        return False
    patterns = [
        r"^[A-Z]{1,5}\(?[A-Z]*\)?[/\-\.]\d{1,6}[/\-\.]\d{4}$",  # WP(C)/1234/2024
        r"^[A-Z]{1,5}\.[A-Z]{1,5}\.?[/\-]\d{1,6}[/\-]\d{4}$",   # CRL.A./567/2023
        r"^[A-Z]{2,10}\d{0,4}[/\-]\d{1,6}[/\-]\d{4}$",           # BAIL1234/567/2024
        r"^\d{1,6}[/\-]\d{4}$",                                    # Simple: 1234/2024
    ]
    case_number = case_number.strip().upper()
    return any(re.match(p, case_number) for p in patterns)


def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone number (+91XXXXXXXXXX or 10 digits)."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    patterns = [
        r"^\+91[6-9]\d{9}$",    # +91 followed by 10 digits
        r"^91[6-9]\d{9}$",      # 91 without plus
        r"^0?[6-9]\d{9}$",      # 10 digits with optional leading 0
    ]
    return any(re.match(p, phone) for p in patterns)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_date_range(date_from: Optional[date], date_to: Optional[date]) -> bool:
    """Validate that date_from is before or equal to date_to."""
    if date_from and date_to:
        return date_from <= date_to
    return True


def validate_court_name(court_name: str) -> bool:
    """Validate court name against known Indian courts."""
    known_courts = [
        "supreme court of india",
        "delhi high court",
        "bombay high court",
        "madras high court",
        "calcutta high court",
        "karnataka high court",
        "allahabad high court",
        "andhra pradesh high court",
        "telangana high court",
        "kerala high court",
        "punjab and haryana high court",
        "rajasthan high court",
        "gujarat high court",
        "orissa high court",
        "patna high court",
        "gauhati high court",
        "jharkhand high court",
        "chhattisgarh high court",
        "uttarakhand high court",
        "himachal pradesh high court",
        "jammu and kashmir high court",
        "meghalaya high court",
        "manipur high court",
        "tripura high court",
        "sikkim high court",
    ]
    return court_name.strip().lower() in known_courts


def sanitize_input(text: str) -> str:
    """Sanitize user input by removing potentially harmful characters."""
    if not text:
        return ""
    # Remove control characters and excessive whitespace
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Remove potential script injection
    text = re.sub(r"<[^>]*>", "", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sanitize_case_number(case_number: str) -> str:
    """Normalize case number format."""
    case_number = case_number.strip().upper()
    # Normalize separators
    case_number = case_number.replace("\\", "/")
    return case_number


def parse_date_string(date_str: str) -> Optional[date]:
    """Parse various Indian date formats to date object."""
    formats = [
        "%Y-%m-%d",       # ISO: 2024-01-15
        "%d-%m-%Y",       # DD-MM-YYYY: 15-01-2024
        "%d/%m/%Y",       # DD/MM/YYYY: 15/01/2024
        "%d.%m.%Y",       # DD.MM.YYYY: 15.01.2024
        "%d %B %Y",       # DD Month YYYY: 15 January 2024
        "%d %b %Y",       # DD Mon YYYY: 15 Jan 2024
        "%B %d, %Y",      # Month DD, YYYY: January 15, 2024
    ]
    date_str = date_str.strip()
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def validate_pagination(page: int, limit: int) -> tuple:
    """Validate and normalize pagination parameters."""
    page = max(1, page)
    limit = max(1, min(100, limit))  # Between 1 and 100
    return page, limit


def validate_bar_council_id(bar_id: str) -> bool:
    """Validate Bar Council registration ID format (e.g., DL/1234/2020)."""
    pattern = r"^[A-Z]{2}/\d{1,6}/\d{4}$"
    return bool(re.match(pattern, bar_id.strip().upper()))
