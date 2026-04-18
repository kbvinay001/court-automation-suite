"""
High Court Scraper - Scrape case data from Indian High Court websites.
"""

import re
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, date, timezone

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Court website URLs
COURT_URLS = {
    "Delhi High Court": "https://delhihighcourt.nic.in",
    "Bombay High Court": "https://bombayhighcourt.nic.in",
    "Madras High Court": "https://www.mhc.tn.gov.in",
    "Calcutta High Court": "https://calcuttahighcourt.gov.in",
    "Karnataka High Court": "https://karnatakajudiciary.kar.nic.in",
    "Allahabad High Court": "https://www.allahabadhighcourt.in",
    "Kerala High Court": "https://highcourtofkerala.nic.in",
    "Punjab and Haryana High Court": "https://phhc.gov.in",
    "Rajasthan High Court": "https://hcraj.nic.in",
    "Gujarat High Court": "https://gujarathighcourt.nic.in",
}


class HighCourtScraper:
    """Scrape case information from Indian High Court websites."""

    def __init__(self, court_name: str = "Delhi High Court"):
        self.court_name = court_name
        self.base_url = COURT_URLS.get(court_name, "")
        self.session_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def scrape_case(self, case_number: str) -> Optional[Dict]:
        """
        Scrape case details from court website.
        Returns case data dict or None if not found.
        """
        logger.info(f"Scraping case {case_number} from {self.court_name}")

        try:
            async with httpx.AsyncClient(
                timeout=30, headers=self.session_headers, follow_redirects=True
            ) as client:
                # Step 1: Get the search page and any CSRF/session tokens
                search_url = f"{self.base_url}/case-status"
                search_page = await client.get(search_url)

                if search_page.status_code != 200:
                    logger.warning(f"Search page returned {search_page.status_code}")
                    return None

                # Step 2: Parse the search form
                soup = BeautifulSoup(search_page.text, "html.parser")
                form = soup.find("form", {"id": "case_search"}) or soup.find("form")

                # Extract hidden fields (CSRF tokens, etc.)
                hidden_fields = {}
                if form:
                    for inp in form.find_all("input", {"type": "hidden"}):
                        name = inp.get("name", "")
                        value = inp.get("value", "")
                        if name:
                            hidden_fields[name] = value

                # Step 3: Parse case number into components
                case_parts = self._parse_case_number(case_number)

                # Step 4: Submit search
                search_data = {
                    **hidden_fields,
                    "case_type": case_parts.get("case_type", ""),
                    "case_number": case_parts.get("number", ""),
                    "case_year": case_parts.get("year", ""),
                }

                result_page = await client.post(
                    f"{self.base_url}/case-status/search",
                    data=search_data,
                )

                if result_page.status_code != 200:
                    logger.warning(f"Search returned {result_page.status_code}")
                    return None

                # Step 5: Parse results
                return self._parse_case_page(result_page.text, case_number)

        except httpx.TimeoutException:
            logger.error(f"Timeout scraping {case_number}")
            return None
        except Exception as e:
            logger.error(f"Error scraping {case_number}: {e}")
            return None

    def _parse_case_number(self, case_number: str) -> Dict:
        """Parse case number into type, number, and year components."""
        # Match patterns like WP(C)/1234/2024 or CRL.A./567/2023
        match = re.match(
            r"^([A-Z\.\(\)]+)[/\-](\d+)[/\-](\d{4})$",
            case_number.strip().upper(),
        )
        if match:
            return {
                "case_type": match.group(1),
                "number": match.group(2),
                "year": match.group(3),
            }
        # Simple format: number/year
        match = re.match(r"^(\d+)[/\-](\d{4})$", case_number.strip())
        if match:
            return {"case_type": "", "number": match.group(1), "year": match.group(2)}

        return {"case_type": "", "number": case_number, "year": ""}

    def _parse_case_page(self, html: str, case_number: str) -> Optional[Dict]:
        """Parse case details from HTML response."""
        soup = BeautifulSoup(html, "html.parser")

        # Look for case details in common table structures
        case_data: Dict[str, Any] = {
            "case_number": case_number.upper(),
            "court_type": "high_court",
            "court_name": self.court_name,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        # Try to find data in table rows
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    if "petitioner" in label:
                        case_data["petitioner"] = value
                    elif "respondent" in label:
                        case_data["respondent"] = value
                    elif "advocate" in label and "petitioner" in label:
                        case_data["advocate_petitioner"] = value
                    elif "advocate" in label and "respondent" in label:
                        case_data["advocate_respondent"] = value
                    elif "status" in label:
                        case_data["status"] = self._map_status(value)
                    elif "filing" in label and "date" in label:
                        case_data["filing_date"] = self._parse_date(value)
                    elif "next" in label and "date" in label:
                        case_data["next_hearing_date"] = self._parse_date(value)
                    elif "subject" in label or "matter" in label:
                        case_data["subject"] = value
                    elif "bench" in label or "judge" in label:
                        case_data["bench"] = value
                    elif "act" in label:
                        case_data["act"] = value

        # Parse hearing history
        case_data["hearings"] = self._parse_hearing_history(soup)

        # Validate we got minimum required data
        if not case_data.get("petitioner"):
            # Try alternative parsing
            return self._parse_alternative_format(soup, case_data)

        return case_data

    def _parse_hearing_history(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract hearing history from page."""
        hearings = []
        # Look for hearing/order history tables
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
            if any(h in " ".join(headers) for h in ["hearing", "order", "date"]):
                rows = table.find_all("tr")[1:]  # Skip header
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        hearing = {
                            "date": self._parse_date(cells[0].get_text(strip=True)),
                        }
                        if len(cells) >= 3:
                            hearing["order_summary"] = cells[2].get_text(strip=True)
                        if len(cells) >= 4:
                            hearing["next_date"] = self._parse_date(cells[3].get_text(strip=True))
                        hearings.append(hearing)
        return hearings

    def _parse_alternative_format(self, soup: BeautifulSoup, case_data: Dict) -> Optional[Dict]:
        """Try alternative HTML parsing strategies."""
        # Look for div-based layouts
        for div in soup.find_all("div", class_=re.compile(r"case|detail|result", re.I)):
            text = div.get_text(separator="\n", strip=True)
            lines = text.split("\n")
            for i, line in enumerate(lines):
                lower = line.lower().strip()
                if "petitioner" in lower and i + 1 < len(lines):
                    case_data["petitioner"] = lines[i + 1].strip()
                elif "respondent" in lower and i + 1 < len(lines):
                    case_data["respondent"] = lines[i + 1].strip()

        return case_data if case_data.get("petitioner") else None

    @staticmethod
    def _map_status(status_text: str) -> str:
        """Map court website status to our status enum."""
        status_lower = status_text.lower().strip()
        mapping = {
            "pending": "pending",
            "disposed": "disposed",
            "listed": "listed",
            "heard": "heard",
            "adjourned": "adjourned",
            "reserved": "reserved",
            "dismissed": "disposed",
            "allowed": "disposed",
            "part heard": "heard",
        }
        for key, value in mapping.items():
            if key in status_lower:
                return value
        return "pending"

    @staticmethod
    def _parse_date(date_str: str) -> Optional[str]:
        """Parse date string into ISO format."""
        if not date_str:
            return None
        formats = ["%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date().isoformat()
            except ValueError:
                continue
        return None

    async def scrape_multiple(self, case_numbers: List[str]) -> List[Dict]:
        """Scrape multiple cases."""
        results = []
        for cn in case_numbers:
            result = await self.scrape_case(cn)
            if result:
                results.append(result)
        return results
