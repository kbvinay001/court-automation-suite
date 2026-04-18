"""
Seed Data Script - Populate database with sample data for development and testing.
"""

import asyncio
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from utils.database import connect_db, close_db, insert_one, insert_many


# ─────────────────── SAMPLE DATA ───────────────────

SAMPLE_CASES = [
    {
        "case_number": "WP(C)/1234/2024",
        "court_type": "high_court",
        "court_name": "Delhi High Court",
        "case_type": "Writ Petition (Civil)",
        "status": "pending",
        "petitioner": "Rajesh Kumar",
        "respondent": "Union of India",
        "advocate_petitioner": "Adv. Sharma & Associates",
        "advocate_respondent": "Additional Solicitor General",
        "filing_date": "2024-01-15",
        "next_hearing_date": (date.today() + timedelta(days=7)).isoformat(),
        "subject": "Right to Information - Non-compliance",
        "bench": "Hon'ble Justice A.K. Sikri",
        "act": "Right to Information Act, 2005",
        "hearings": [
            {"date": "2024-02-10", "order_summary": "Notice issued to respondents"},
            {"date": "2024-03-15", "order_summary": "Respondent filed counter affidavit"},
            {"date": "2024-04-20", "order_summary": "Arguments heard, adjourned"},
        ],
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "case_number": "CRL.A./567/2023",
        "court_type": "high_court",
        "court_name": "Bombay High Court",
        "case_type": "Criminal Appeal",
        "status": "listed",
        "petitioner": "State of Maharashtra",
        "respondent": "Anil Verma",
        "advocate_petitioner": "Public Prosecutor",
        "advocate_respondent": "Adv. Patel & Partners",
        "filing_date": "2023-08-20",
        "next_hearing_date": (date.today() + timedelta(days=3)).isoformat(),
        "subject": "Appeal against acquittal - IPC 420",
        "bench": "Hon'ble Justice B.N. Srikrishna",
        "act": "Indian Penal Code, 1860",
        "hearings": [
            {"date": "2023-10-05", "order_summary": "Appeal admitted"},
            {"date": "2023-12-12", "order_summary": "Record called from trial court"},
            {"date": "2024-02-18", "order_summary": "Arguments in progress"},
        ],
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "case_number": "CS/890/2024",
        "court_type": "district_court",
        "court_name": "District Court - Saket, Delhi",
        "case_type": "Civil Suit",
        "status": "pending",
        "petitioner": "M/s XYZ Enterprises",
        "respondent": "ABC Corporation Ltd.",
        "advocate_petitioner": "Adv. Singh & Co.",
        "advocate_respondent": "Adv. Gupta Chambers",
        "filing_date": "2024-03-01",
        "next_hearing_date": (date.today() + timedelta(days=14)).isoformat(),
        "subject": "Recovery of dues - Commercial dispute",
        "bench": "Sh. R.K. Arora, ADJ",
        "act": "Commercial Courts Act, 2015",
        "hearings": [
            {"date": "2024-04-10", "order_summary": "Summons issued to defendant"},
        ],
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "case_number": "SLP(C)/1122/2024",
        "court_type": "supreme_court",
        "court_name": "Supreme Court of India",
        "case_type": "Special Leave Petition (Civil)",
        "status": "pending",
        "petitioner": "People's Union for Civil Liberties",
        "respondent": "Government of India",
        "advocate_petitioner": "Senior Adv. Datar",
        "advocate_respondent": "Attorney General of India",
        "filing_date": "2024-02-14",
        "next_hearing_date": (date.today() + timedelta(days=21)).isoformat(),
        "subject": "Right to Privacy - Data Protection",
        "bench": "Hon'ble CJI & Justice Kaul",
        "act": "Constitution of India, Article 21",
        "hearings": [
            {"date": "2024-03-20", "order_summary": "Leave granted, notice issued"},
        ],
        "created_at": datetime.utcnow().isoformat(),
    },
]

SAMPLE_USERS = [
    {
        "name": "Demo Advocate",
        "email": "demo@courtautomation.in",
        "phone": "+919876543210",
        "role": "advocate",
        "is_active": True,
        "notification_preferences": {
            "email": True,
            "whatsapp": True,
            "sms": False,
            "daily_digest": True,
        },
        "tracked_cases": ["WP(C)/1234/2024", "CS/890/2024"],
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "name": "Test Litigant",
        "email": "litigant@example.com",
        "phone": "+919876543211",
        "role": "litigant",
        "is_active": True,
        "notification_preferences": {
            "email": True,
            "whatsapp": False,
            "sms": False,
            "daily_digest": False,
        },
        "tracked_cases": ["WP(C)/1234/2024"],
        "created_at": datetime.utcnow().isoformat(),
    },
]


def generate_causelist_entries() -> list:
    """Generate sample cause list entries for today."""
    today = date.today()
    entries = []
    cases = [
        ("WP(C)/1234/2024", "Rajesh Kumar", "Union of India"),
        ("CRL.A./567/2023", "State of Maharashtra", "Anil Verma"),
        ("CS/100/2024", "M/s Tech Solutions", "Innovation Corp"),
        ("WP(C)/2001/2024", "Citizens Forum", "State of Delhi"),
        ("CS/555/2024", "Ram Enterprises", "Shyam Trading Co."),
    ]
    for i, (cn, pet, resp) in enumerate(cases, 1):
        entries.append({
            "serial_number": i,
            "case_number": cn,
            "petitioner": pet,
            "respondent": resp,
            "listing_date": today.isoformat(),
            "court_number": "1",
        })
    return [
        {
            "court_name": "Delhi High Court",
            "date": today.isoformat(),
            "court_number": "1",
            "bench": "Hon'ble Justice A.K. Sikri",
            "total_cases": len(entries),
            "entries": entries,
            "scraped_at": datetime.utcnow().isoformat(),
        }
    ]


async def seed_database():
    """Seed the database with sample data."""
    print("🌱 Seeding database...")

    await connect_db()

    # Insert cases
    print(f"  📋 Inserting {len(SAMPLE_CASES)} sample cases...")
    for case in SAMPLE_CASES:
        await insert_one("cases", case)

    # Insert users
    print(f"  👤 Inserting {len(SAMPLE_USERS)} sample users...")
    for user in SAMPLE_USERS:
        await insert_one("users", user)

    # Insert tracked cases
    print("  🔔 Setting up tracked cases...")
    tracked = [
        {
            "user_id": "demo_user",
            "case_number": "WP(C)/1234/2024",
            "court_name": "Delhi High Court",
            "is_active": True,
            "tracked_at": datetime.utcnow().isoformat(),
        },
        {
            "user_id": "demo_user",
            "case_number": "CS/890/2024",
            "court_name": "District Court - Saket, Delhi",
            "is_active": True,
            "tracked_at": datetime.utcnow().isoformat(),
        },
    ]
    for t in tracked:
        await insert_one("tracked_cases", t)

    # Insert cause lists
    print("  📅 Inserting sample cause lists...")
    causelists = generate_causelist_entries()
    for cl in causelists:
        await insert_one("causelists", cl)

    await close_db()
    print("✅ Database seeded successfully!")
    print(f"   Cases: {len(SAMPLE_CASES)}")
    print(f"   Users: {len(SAMPLE_USERS)}")
    print(f"   Tracked: {len(tracked)}")
    print(f"   Cause Lists: {len(causelists)}")


if __name__ == "__main__":
    asyncio.run(seed_database())
