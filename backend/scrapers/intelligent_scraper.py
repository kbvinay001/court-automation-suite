"""
Intelligent Scraper - AI-powered adaptive web scraper that learns page structures.
"""

import re
import json
import hashlib
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class PageStructure:
    """Represents the learned structure of a court webpage."""

    def __init__(self, url: str):
        self.url = url
        self.field_selectors: Dict[str, str] = {}  # field_name -> CSS selector
        self.table_patterns: List[Dict] = []
        self.form_selectors: Dict[str, str] = {}
        self.last_updated: str = datetime.now(timezone.utc).isoformat()
        self.confidence: float = 0.0
        self.success_count: int = 0
        self.failure_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "field_selectors": self.field_selectors,
            "table_patterns": self.table_patterns,
            "form_selectors": self.form_selectors,
            "last_updated": self.last_updated,
            "confidence": self.confidence,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PageStructure":
        ps = cls(data["url"])
        ps.field_selectors = data.get("field_selectors", {})
        ps.table_patterns = data.get("table_patterns", [])
        ps.form_selectors = data.get("form_selectors", {})
        ps.confidence = data.get("confidence", 0.0)
        ps.success_count = data.get("success_count", 0)
        ps.failure_count = data.get("failure_count", 0)
        return ps


class IntelligentScraper:
    """AI-powered scraper that adapts to page structure changes."""

    LEGAL_FIELDS = [
        "case_number", "petitioner", "respondent",
        "advocate_petitioner", "advocate_respondent",
        "filing_date", "next_hearing_date", "status",
        "bench", "judge", "court_number", "subject",
        "act", "section", "order_summary",
    ]

    FIELD_KEYWORDS = {
        "case_number": ["case no", "case number", "cnr", "case id"],
        "petitioner": ["petitioner", "appellant", "plaintiff", "complainant"],
        "respondent": ["respondent", "defendant", "opposite party", "accused"],
        "advocate_petitioner": ["petitioner advocate", "advocate for petitioner", "pet. adv"],
        "advocate_respondent": ["respondent advocate", "advocate for respondent", "resp. adv"],
        "filing_date": ["filing date", "date of filing", "registration date", "filed on"],
        "next_hearing_date": ["next date", "next hearing", "adjourned to", "listed on"],
        "status": ["case status", "status", "disposal", "nature of disposal"],
        "bench": ["bench", "coram", "before"],
        "judge": ["judge", "hon'ble", "justice"],
        "court_number": ["court no", "court number", "room no"],
        "subject": ["subject", "matter", "nature of case"],
        "act": ["act", "under act", "statute"],
        "section": ["section", "under section", "provision"],
    }

    def __init__(self):
        self._learned_structures: Dict[str, PageStructure] = {}
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        }

    def _get_url_key(self, url: str) -> str:
        """Generate a unique key for a URL pattern."""
        return hashlib.md5(url.encode()).hexdigest()[:12]  # type: ignore[index]

    async def scrape_url(self, url: str, target_fields: Optional[List[str]] = None) -> Dict:  # type: ignore[return-value]
        """
        Intelligently scrape a URL, learning and adapting to its structure.
        """
        target_fields = target_fields or self.LEGAL_FIELDS
        url_key = self._get_url_key(url)

        try:
            async with httpx.AsyncClient(
                timeout=30, headers=self.headers, follow_redirects=True
            ) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return {"error": f"HTTP {response.status_code}"}

                soup = BeautifulSoup(response.text, "html.parser")

                # Try learned selectors first
                if url_key in self._learned_structures:
                    structure = self._learned_structures[url_key]
                    result = self._apply_learned_selectors(soup, structure, target_fields)
                    if self._is_result_valid(result, target_fields):
                        structure.success_count += 1
                        structure.confidence = min(
                            1.0,
                            structure.success_count / max(
                                structure.success_count + structure.failure_count, 1
                            ),
                        )
                        return result
                    else:
                        structure.failure_count += 1

                # Learn new structure
                logger.info(f"Learning page structure for {url}")
                result, new_structure = self._analyze_and_extract(soup, url, target_fields)
                self._learned_structures[url_key] = new_structure

                return result

        except Exception as e:
            logger.error(f"Intelligent scrape failed for {url}: {e}")
            return {"error": str(e)}

    def _apply_learned_selectors(
        self, soup: BeautifulSoup, structure: PageStructure,
        target_fields: List[str],
    ) -> Dict:
        """Apply previously learned CSS selectors."""
        result = {}
        for field in target_fields:
            selector = structure.field_selectors.get(field)
            if selector:
                try:
                    element = soup.select_one(selector)
                    if element:
                        result[field] = element.get_text(strip=True)
                except Exception:
                    pass
        return result

    def _analyze_and_extract(
        self, soup: BeautifulSoup, url: str, target_fields: List[str]
    ) -> tuple:
        """Analyze page structure and extract data."""
        structure = PageStructure(url)
        result = {}

        # Strategy 1: Table-based extraction (most common for court sites)
        table_results = self._extract_from_tables(soup, target_fields, structure)
        result.update(table_results)

        # Strategy 2: Label-value pair extraction
        label_results = self._extract_label_value_pairs(soup, target_fields, structure)
        for field, value in label_results.items():
            if field not in result:
                result[field] = value

        # Strategy 3: Definition list extraction
        dl_results = self._extract_from_definition_lists(soup, target_fields, structure)
        for field, value in dl_results.items():
            if field not in result:
                result[field] = value

        # Strategy 4: Div-based extraction
        div_results = self._extract_from_divs(soup, target_fields, structure)
        for field, value in div_results.items():
            if field not in result:
                result[field] = value

        structure.confidence = len(result) / max(len(target_fields), 1)
        return result, structure

    def _extract_from_tables(
        self, soup: BeautifulSoup, target_fields: List[str],
        structure: PageStructure,
    ) -> Dict:
        """Extract data from HTML tables using keyword matching."""
        result = {}
        tables = soup.find_all("table")

        for table_idx, table in enumerate(tables):
            rows = table.find_all("tr")
            for row_idx, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    matched_field = self._match_field(label, target_fields)
                    if matched_field and value:
                        result[matched_field] = value
                        # Learn the selector
                        selector = f"table:nth-of-type({table_idx + 1}) tr:nth-of-type({row_idx + 1}) td:nth-of-type(2)"
                        structure.field_selectors[matched_field] = selector
        return result

    def _extract_label_value_pairs(
        self, soup: BeautifulSoup, target_fields: List[str],
        structure: PageStructure,
    ) -> Dict:
        """Extract from label: value patterns in any element."""
        result = {}
        all_text_elements = soup.find_all(["p", "span", "div", "li", "strong", "b"])

        for elem in all_text_elements:
            text = elem.get_text(strip=True)
            # Look for "Label: Value" or "Label - Value" patterns
            match = re.match(r"^([^:]+):\s*(.+)$", text)
            if not match:
                match = re.match(r"^([^-]+)\s*[-–]\s*(.+)$", text)
            if match:
                label = match.group(1).strip().lower()
                value = match.group(2).strip()
                matched_field = self._match_field(label, target_fields)
                if matched_field and value and matched_field not in result:
                    result[matched_field] = value
        return result

    def _extract_from_definition_lists(
        self, soup: BeautifulSoup, target_fields: List[str],
        structure: PageStructure,
    ) -> Dict:
        """Extract from HTML definition lists."""
        result = {}
        for dl in soup.find_all("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            for dt, dd in zip(dts, dds):
                label = dt.get_text(strip=True).lower()
                value = dd.get_text(strip=True)
                matched_field = self._match_field(label, target_fields)
                if matched_field and value:
                    result[matched_field] = value
        return result

    def _extract_from_divs(
        self, soup: BeautifulSoup, target_fields: List[str],
        structure: PageStructure,
    ) -> Dict:
        """Extract from div-based layouts with class/id hints."""
        result = {}
        for field in target_fields:
            if field in result:
                continue
            keywords = self.FIELD_KEYWORDS.get(field, [field])
            for keyword in keywords:
                clean = keyword.replace(" ", "[-_\\s]*")
                divs = soup.find_all(
                    ["div", "span", "td"],
                    class_=re.compile(clean, re.I),
                )
                for div in divs:
                    value = div.get_text(strip=True)
                    if value and len(value) < 500:
                        result[field] = value
                        break
                if field in result:
                    break
        return result

    def _match_field(self, label: str, target_fields: List[str]) -> Optional[str]:
        """Match a label text to a target field name using keyword matching."""
        label_lower = label.lower().strip()
        for field in target_fields:
            keywords = self.FIELD_KEYWORDS.get(field, [field.replace("_", " ")])
            for keyword in keywords:
                if keyword in label_lower:
                    return field
        return None

    def _is_result_valid(self, result: Dict, target_fields: List[str]) -> bool:
        """Check if extracted result has enough fields to be useful."""
        extracted = sum(1 for f in target_fields if f in result and result[f])
        return extracted >= 2  # At least 2 fields extracted

    def get_learned_structures(self) -> Dict[str, Dict]:
        """Get all learned page structures."""
        return {k: v.to_dict() for k, v in self._learned_structures.items()}

    async def save_structures(self):
        """Persist learned structures to database."""
        from utils.database import update_one, find_one, insert_one

        for url_key, structure in self._learned_structures.items():
            data = structure.to_dict()
            existing = await find_one("page_structures", {"url_key": url_key})
            if existing:
                await update_one("page_structures", {"url_key": url_key}, data)
            else:
                data["url_key"] = url_key
                await insert_one("page_structures", data)

    async def load_structures(self):
        """Load previously learned structures from database."""
        from utils.database import find_many

        docs = await find_many("page_structures", {}, limit=100)
        for doc in docs:
            url_key = doc.get("url_key", "")
            if url_key:
                self._learned_structures[url_key] = PageStructure.from_dict(doc)
        logger.info(f"Loaded {len(self._learned_structures)} learned page structures")
