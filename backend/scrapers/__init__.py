# Court Automation Suite - Scrapers Package

from scrapers.high_court_scraper import HighCourtScraper
from scrapers.district_court_scraper import DistrictCourtScraper
from scrapers.causelist_scraper import CauseListScraper
from scrapers.intelligent_scraper import IntelligentScraper


def get_scraper(court_type: str, court_name: str):
    """Factory function to get the appropriate scraper for a court."""
    if court_type == "high_court":
        return HighCourtScraper(court_name)
    elif court_type == "district_court":
        # Parse state/district from court name
        parts = court_name.replace("District Court - ", "").split(", ")
        district = parts[0] if parts else "New Delhi"
        state = parts[1] if len(parts) > 1 else "Delhi"
        return DistrictCourtScraper(state=state, district=district)
    elif court_type == "supreme_court":
        return HighCourtScraper("Supreme Court of India")
    else:
        return IntelligentScraper()


__all__ = [
    "HighCourtScraper", "DistrictCourtScraper",
    "CauseListScraper", "IntelligentScraper",
    "get_scraper",
]
