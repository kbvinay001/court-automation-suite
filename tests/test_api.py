"""
Tests for API models, validators, routes, and services.
"""
import pytest
from datetime import date


# ─── Validators ───────────────────────────────────────────────────

class TestValidators:
    def test_validate_case_number_valid(self):
        from utils.validators import validate_case_number
        assert validate_case_number("WP(C)/1234/2024") is True

    def test_validate_case_number_invalid(self):
        from utils.validators import validate_case_number
        assert validate_case_number(None) is False
        assert validate_case_number("") is False
        assert validate_case_number("invalid") is False

    def test_validate_phone_number(self):
        from utils.validators import validate_phone_number
        assert validate_phone_number("+919876543210") is True
        assert validate_phone_number("9876543210") is True
        assert validate_phone_number("12345") is False

    def test_validate_email(self):
        from utils.validators import validate_email
        assert validate_email("test@example.com") is True
        assert validate_email("invalid") is False

    def test_sanitize_input(self):
        from utils.validators import sanitize_input
        assert sanitize_input("<script>alert('xss')</script>") == "alert('xss')"
        assert sanitize_input("  hello  world  ") == "hello world"
        assert sanitize_input("") == ""

    def test_validate_date_range(self):
        from utils.validators import validate_date_range
        assert validate_date_range(date(2024, 1, 1), date(2024, 12, 31)) is True
        assert validate_date_range(date(2024, 12, 31), date(2024, 1, 1)) is False
        assert validate_date_range(None, None) is True

    def test_validate_pagination(self):
        from utils.validators import validate_pagination
        assert validate_pagination(1, 20) == (1, 20)
        assert validate_pagination(-1, 200) == (1, 100)
        assert validate_pagination(0, 0) == (1, 1)


# ─── Data Models ──────────────────────────────────────────────────

class TestDataModels:
    def test_case_model_creation(self):
        from api.models.case import Case, CaseStatus
        case = Case(
            case_number="WP(C)/1234/2024",
            court_name="Delhi High Court",
            petitioner="Ram Kumar",
            respondent="State of Delhi",
        )
        assert case.case_number == "WP(C)/1234/2024"
        assert case.status == CaseStatus.PENDING

    def test_case_status_enum(self):
        from api.models.case import CaseStatus
        assert CaseStatus.PENDING.value == "pending"
        assert CaseStatus.DISPOSED.value == "disposed"

    def test_user_model(self):
        from api.models.user import UserCreate
        user = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="securepassword123",
        )
        assert user.full_name == "Test User"
        assert user.email == "test@example.com"

    def test_causelist_model(self):
        from api.models.causelist import CauseList
        cl = CauseList(
            court_name="Delhi High Court",
            list_date=date(2024, 1, 15),
        )
        assert cl.court_name == "Delhi High Court"
        assert cl.total_cases == 0


# ─── API Routes ───────────────────────────────────────────────────

class TestAPIRoutes:
    def test_scraper_router_exists(self):
        from api.routes.court_scraper import router
        assert router is not None

    def test_causelist_router_exists(self):
        from api.routes.causelist import router
        assert router is not None

    def test_analytics_router_exists(self):
        from api.routes.analytics import router
        assert router is not None


# ─── Services ─────────────────────────────────────────────────────

class TestServices:
    def test_pdf_generator_init(self):
        from api.services.pdf_generator import PDFGenerator
        gen = PDFGenerator()
        assert gen is not None

    def test_notification_service_init(self):
        from api.services.notification_service import NotificationService
        svc = NotificationService()
        assert svc is not None

    def test_ai_service_init(self):
        from api.services.ai_service import AIService
        svc = AIService()
        assert svc is not None

    def test_scraper_service_init(self):
        from api.services.scraper_service import ScraperService
        svc = ScraperService()
        assert svc is not None
