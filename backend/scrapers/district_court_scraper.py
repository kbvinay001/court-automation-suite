"""
District Court Scraper - Scrape case data from eCourts (district courts) platform.
"""

import re
import logging
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

ECOURTS_BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6"


class DistrictCourtScraper:
    """Scrape case information from eCourts India platform (district courts)."""

    def __init__(self, state: str = "Delhi", district: str = "New Delhi"):
        self.state = state
        self.district = district
        self.base_url = ECOURTS_BASE_URL
        self.session_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": ECOURTS_BASE_URL,
        }
        self.state_codes = {
            "Delhi": "6", "Maharashtra": "14", "Tamil Nadu": "25",
            "West Bengal": "28", "Karnataka": "12", "Uttar Pradesh": "26",
            "Rajasthan": "22", "Gujarat": "9", "Kerala": "13",
            "Andhra Pradesh": "1", "Telangana": "36", "Bihar": "4",
            "Punjab": "21", "Haryana": "10", "Odisha": "20",
        }

    async def scrape_case(self, case_number: str) -> Optional[Dict]:
        """Scrape case from eCourts India platform."""
        logger.info(f"Scraping district court case {case_number} ({self.state}/{self.district})")

        try:
            async with httpx.AsyncClient(
                timeout=30, headers=self.session_headers, follow_redirects=True
            ) as client:
                # Step 1: Get initial page for captcha/tokens
                init_response = await client.get(f"{self.base_url}/")
                if init_response.status_code != 200:
                    logger.warning("eCourts initial page failed")
                    return None

                # Extract session tokens
                soup = BeautifulSoup(init_response.text, "html.parser")
                csrf_token = self._extract_token(soup)

                # Step 2: Set state and district
                state_code = self.state_codes.get(self.state, "6")

                # Step 3: Submit case number search
                case_parts = self._parse_case_number(case_number)
                search_data = {
                    "state_code": state_code,
                    "dist_code": "1",
                    "court_complex_code": "",
                    "case_type": case_parts.get("case_type", ""),
                    "case_no": case_parts.get("number", ""),
                    "case_year": case_parts.get("year", ""),
                    "csrf_token": csrf_token,
                }

                result_response = await client.post(
                    f"{self.base_url}/cases/case_no.php",
                    data=search_data,
                )

                if result_response.status_code != 200:
                    return None

                return self._parse_ecourts_response(result_response.text, case_number)

        except httpx.TimeoutException:
            logger.error(f"Timeout scraping {case_number}")
            return None
        except Exception as e:
            logger.error(f"Error scraping district court case: {e}")
            return None

    def _extract_token(self, soup: BeautifulSoup) -> str:
        """Extract CSRF or session token from page."""
        token_input = soup.find("input", {"name": "csrf_token"})
        if token_input:
            return token_input.get("value", "")
        meta = soup.find("meta", {"name": "csrf-token"})
        if meta:
            return meta.get("content", "")
        return ""

    def _parse_case_number(self, case_number: str) -> Dict:
        """Parse eCourts case number format."""
        match = re.match(r"^([A-Z\s]+)[/\-](\d+)[/\-](\d{4})$", case_number.upper().strip())
        if match:
            return {
                "case_type": match.group(1).strip(),
                "number": match.group(2),
                "year": match.group(3),
            }
        match = re.match(r"^(\d+)[/\-](\d{4})$", case_number.strip())
        if match:
            return {"case_type": "", "number": match.group(1), "year": match.group(2)}
        return {"case_type": "", "number": case_number, "year": ""}

    def _parse_ecourts_response(self, html: str, case_number: str) -> Optional[Dict]:
        """Parse eCourts search result page."""
        soup = BeautifulSoup(html, "html.parser")

        case_data: Dict[str, Any] = {
            "case_number": case_number.upper(),
            "court_type": "district_court",
            "court_name": f"District Court - {self.district}, {self.state}",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

        # eCourts uses specific table structures
        detail_table = soup.find("table", {"class": re.compile(r"case_det|table", re.I)})
        if detail_table:
            rows = detail_table.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    self._map_field(case_data, label, value)

        # Parse hearing/order details
        case_data["hearings"] = self._parse_orders(soup)

        # Look for case status in result links
        status_div = soup.find("div", class_=re.compile(r"status|disposed", re.I))
        if status_div:
            status_text = status_div.get_text(strip=True)
            case_data["status"] = self._map_status(status_text)

        return case_data if case_data.get("petitioner") else None

    def _map_field(self, case_data: Dict, label: str, value: str):
        """Map eCourts field label to case data dict."""
        field_map = {
            "petitioner": "petitioner",
            "respondent": "respondent",
            "filing date": "filing_date",
            "registration date": "filing_date",
            "next hearing": "next_hearing_date",
            "next date": "next_hearing_date",
            "case status": "status",
            "nature of disposal": "status",
            "petitioner advocate": "advocate_petitioner",
            "respondent advocate": "advocate_respondent",
            "under act": "act",
            "under section": "section",
            "judge": "bench",
            "court number": "court_number",
        }
        for key, field in field_map.items():
            if key in label:
                if "date" in key:
                    case_data[field] = self._parse_date(value)
                elif field == "status":
                    case_data[field] = self._map_status(value)
                else:
                    case_data[field] = value
                break

    def _parse_orders(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse order/hearing history from eCourts."""
        hearings = []
        order_table = soup.find("table", {"id": re.compile(r"order|history", re.I)})
        if not order_table:
            order_table = soup.find("table", class_=re.compile(r"order|history", re.I))

        if order_table:
            rows = order_table.find_all("tr")[1:]  # Skip header
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    hearing = {"date": self._parse_date(cells[0].get_text(strip=True))}
                    if len(cells) >= 3:
                        hearing["judge"] = cells[1].get_text(strip=True)
                        hearing["order_summary"] = cells[2].get_text(strip=True)
                    hearings.append(hearing)
        return hearings

    @staticmethod
    def _map_status(status_text: str) -> str:
        """Map eCourts status to our enum."""
        status_lower = status_text.lower()
        if "disposed" in status_lower or "closed" in status_lower:
            return "disposed"
        elif "pending" in status_lower:
            return "pending"
        elif "adjourned" in status_lower:
            return "adjourned"
        return "pending"

    @staticmethod
    def _parse_date(date_str: str) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        for fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(date_str.strip(), fmt).date().isoformat()
            except ValueError:
                continue
        return None

    async def search_by_party_name(self, name: str) -> List[Dict]:
        """Search cases by party name on eCourts."""
        logger.info(f"Searching district court cases for party: {name}")
        try:
            async with httpx.AsyncClient(
                timeout=30, headers=self.session_headers
            ) as client:
                state_code = self.state_codes.get(self.state, "6")
                search_data = {
                    "state_code": state_code,
                    "party_name": name,
                    "search_type": "party",
                }
                response = await client.post(
                    f"{self.base_url}/cases/party_name.php",
                    data=search_data,
                )
                if response.status_code == 200:
                    return self._parse_search_results(response.text)
        except Exception as e:
            logger.error(f"Party name search failed: {e}")
        return []

    def _parse_search_results(self, html: str) -> List[Dict]:
        """Parse search results listing."""
        soup = BeautifulSoup(html, "html.parser")
        results = []
        result_table = soup.find("table", {"id": re.compile(r"result|list", re.I)})
        if result_table:
            rows = result_table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    results.append({
                        "case_number": cells[0].get_text(strip=True),
                        "parties": cells[1].get_text(strip=True),
                        "status": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                    })
        return results
