"""
Tests for court scrapers: HighCourt, DistrictCourt, CauseList, Intelligent, and factory.
"""
import pytest


# ─── High Court Scraper ──────────────────────────────────────────

class TestHighCourtScraper:
    def test_init(self):
        from scrapers.high_court_scraper import HighCourtScraper
        scraper = HighCourtScraper()
        assert scraper is not None

    def test_private_parse_case_number(self):
        from scrapers.high_court_scraper import HighCourtScraper
        scraper = HighCourtScraper()
        result = scraper._parse_case_number("WP(C)/1234/2024")
        assert result is not None
        assert result.get("number") == "1234"

    def test_private_map_status(self):
        from scrapers.high_court_scraper import HighCourtScraper
        scraper = HighCourtScraper()
        assert scraper._map_status("pending") == "pending"
        assert scraper._map_status("disposed") == "disposed"

    def test_private_parse_date(self):
        from scrapers.high_court_scraper import HighCourtScraper
        scraper = HighCourtScraper()
        result = scraper._parse_date("15-01-2024")
        assert result is not None

    def test_court_urls_available(self):
        from scrapers.high_court_scraper import COURT_URLS
        assert isinstance(COURT_URLS, dict)
        assert len(COURT_URLS) > 0

    def test_has_scrape_method(self):
        from scrapers.high_court_scraper import HighCourtScraper
        scraper = HighCourtScraper()
        assert hasattr(scraper, 'scrape_case')


# ─── District Court Scraper ──────────────────────────────────────

class TestDistrictCourtScraper:
    def test_init_defaults(self):
        from scrapers.district_court_scraper import DistrictCourtScraper
        scraper = DistrictCourtScraper()
        assert scraper is not None

    def test_init_custom(self):
        from scrapers.district_court_scraper import DistrictCourtScraper
        scraper = DistrictCourtScraper(state="delhi", district="new_delhi")
        assert scraper.state == "delhi"

    def test_private_parse_case_number(self):
        from scrapers.district_court_scraper import DistrictCourtScraper
        scraper = DistrictCourtScraper()
        result = scraper._parse_case_number("CS/1234/2024")
        assert result is not None

    def test_private_map_status(self):
        from scrapers.district_court_scraper import DistrictCourtScraper
        scraper = DistrictCourtScraper()
        assert scraper._map_status("pending") == "pending"

    def test_has_state_attribute(self):
        from scrapers.district_court_scraper import DistrictCourtScraper
        scraper = DistrictCourtScraper()
        assert hasattr(scraper, 'state')


# ─── Intelligent Scraper ─────────────────────────────────────────

class TestIntelligentScraper:
    def test_init(self):
        from scrapers.intelligent_scraper import IntelligentScraper
        scraper = IntelligentScraper()
        assert scraper is not None

    def test_get_learned_structures(self):
        from scrapers.intelligent_scraper import IntelligentScraper
        scraper = IntelligentScraper()
        # Returns dict of learned structures
        result = scraper.get_learned_structures()
        assert isinstance(result, dict)

    def test_page_structure(self):
        from scrapers.intelligent_scraper import PageStructure
        ps = PageStructure(url="https://example.com")
        assert ps.url == "https://example.com"
        assert isinstance(ps.field_selectors, dict)

    def test_has_scrape_url_method(self):
        from scrapers.intelligent_scraper import IntelligentScraper
        scraper = IntelligentScraper()
        assert hasattr(scraper, 'scrape_url')


# ─── Cause List Scraper ──────────────────────────────────────────

class TestCauseListScraper:
    def test_init(self):
        from scrapers.causelist_scraper import CauseListScraper
        scraper = CauseListScraper()
        assert scraper is not None

    def test_supported_courts(self):
        from scrapers.causelist_scraper import CAUSELIST_URLS
        assert isinstance(CAUSELIST_URLS, dict)
        assert len(CAUSELIST_URLS) > 0


# ─── Scraper Factory ─────────────────────────────────────────────

class TestScraperFactory:
    def test_get_high_court_scraper(self):
        from scrapers import get_scraper
        scraper = get_scraper("high_court", "Delhi High Court")
        assert scraper is not None

    def test_get_district_court_scraper(self):
        from scrapers import get_scraper
        scraper = get_scraper("district_court", "District Court - New Delhi, Delhi")
        assert scraper is not None

    def test_get_intelligent_scraper_fallback(self):
        from scrapers import get_scraper
        scraper = get_scraper("unknown_type", "Some Court")
        assert scraper is not None
