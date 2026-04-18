"""
Cause List Scraper - Scrape daily cause lists from court websites.
"""

import re
import logging
from typing import List, Optional, Dict
from datetime import datetime, date
from io import BytesIO

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("pdfplumber not installed - PDF cause list parsing disabled")


CAUSELIST_URLS = {
    "Delhi High Court": "https://delhihighcourt.nic.in/causelist",
    "Bombay High Court": "https://bombayhighcourt.nic.in/causelist",
    "Madras High Court": "https://www.mhc.tn.gov.in/causelist",
    "Supreme Court of India": "https://www.sci.gov.in/cause-lists",
    "Karnataka High Court": "https://karnatakajudiciary.kar.nic.in/causelist",
    "Allahabad High Court": "https://www.allahabadhighcourt.in/causelist",
    "Calcutta High Court": "https://calcuttahighcourt.gov.in/causelist",
}


class CauseListScraper:
    """Scrape daily cause lists from Indian court websites."""

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        }

    async def scrape_causelist(
        self, court_name: str, target_date: date
    ) -> List:  # type: ignore[return-value]
        """
        Scrape cause list for a court on a given date.
        Returns list of CauseList objects.
        """
        from api.models.causelist import CauseList, CauseListEntry

        logger.info(f"Scraping cause list: {court_name} for {target_date.isoformat()}")

        base_url = CAUSELIST_URLS.get(court_name)
        if not base_url:
            logger.warning(f"No cause list URL for {court_name}")
            return []

        try:
            async with httpx.AsyncClient(
                timeout=30, headers=self.headers, follow_redirects=True
            ) as client:
                # Fetch cause list page
                date_str = target_date.strftime("%d-%m-%Y")
                response = await client.get(
                    base_url, params={"date": date_str}
                )

                if response.status_code != 200:
                    logger.warning(f"Cause list page returned {response.status_code}")
                    return []

                content_type = response.headers.get("content-type", "")

                if "pdf" in content_type.lower():
                    # PDF cause list
                    return await self._parse_pdf_causelist(
                        response.content, court_name, target_date
                    )
                else:
                    # HTML cause list
                    return await self._parse_html_causelist(
                        response.text, court_name, target_date
                    )

        except Exception as e:
            logger.error(f"Error scraping cause list: {e}")
            return []

    async def _parse_html_causelist(
        self, html: str, court_name: str, target_date: date
    ) -> List:
        """Parse HTML-based cause list."""
        from api.models.causelist import CauseList, CauseListEntry

        soup = BeautifulSoup(html, "html.parser")
        cause_lists = []

        # Find PDF links on the page
        pdf_links = self._find_pdf_links(soup, target_date)

        # Find cause list tables
        tables = soup.find_all("table", class_=re.compile(r"cause|list|court", re.I))
        if not tables:
            tables = soup.find_all("table")

        current_court_number = None
        current_bench = None
        entries = []
        serial = 1

        for table in tables:
            # Check for court number/bench header
            prev = table.find_previous(["h2", "h3", "h4", "p", "div"])
            if prev:
                header_text = prev.get_text(strip=True)
                court_match = re.search(r"court\s*(?:no\.?\s*)?(\d+)", header_text, re.I)
                if court_match:
                    # Save previous court's data
                    if entries and current_court_number:
                        cause_lists.append(CauseList(
                            court_name=court_name,
                            list_date=target_date,
                            court_number=current_court_number,
                            bench=current_bench,
                            total_cases=len(entries),
                            entries=entries,
                        ))
                        entries = []
                        serial = 1

                    current_court_number = court_match.group(1)
                    bench_match = re.search(r"(?:justice|hon)\s+(.+)", header_text, re.I)
                    current_bench = bench_match.group(1).strip() if bench_match else None

            # Parse table rows
            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header row
                cells = row.find_all("td")
                if len(cells) >= 3:
                    entry = CauseListEntry(
                        serial_number=serial,
                        case_number=cells[0].get_text(strip=True) if len(cells) > 0 else "",
                        petitioner=cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        respondent=cells[2].get_text(strip=True) if len(cells) > 2 else "",
                        advocate_petitioner=cells[3].get_text(strip=True) if len(cells) > 3 else None,
                        listing_date=target_date,
                        court_number=current_court_number,
                        bench=current_bench,
                    )
                    entries.append(entry)  # type: ignore[attr-defined]
                    serial += 1  # type: ignore[operator]

        # Save last court's entries
        if entries:
            cause_lists.append(CauseList(
                court_name=court_name,
                list_date=target_date,
                court_number=current_court_number or "1",
                bench=current_bench,
                total_cases=len(entries),
                entries=entries,
            ))

        # If no tables found, try PDF links
        if not cause_lists and pdf_links:
            for pdf_url in pdf_links[:5]:  # type: ignore[index]  # Limit to 5 PDFs
                pdf_lists = await self._download_and_parse_pdf(
                    pdf_url, court_name, target_date
                )
                cause_lists.extend(pdf_lists)

        return cause_lists

    async def _parse_pdf_causelist(
        self, pdf_content: bytes, court_name: str, target_date: date
    ) -> List:
        """Parse PDF cause list content."""
        from api.models.causelist import CauseList, CauseListEntry

        if not PDF_AVAILABLE:
            logger.warning("pdfplumber not available for PDF parsing")
            return []

        try:
            entries = []
            serial = 1

            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    # Extract tables from PDF
                    page_tables = page.extract_tables()

                    for table in page_tables:
                        for row in table:
                            if row and len(row) >= 3 and row[0] and row[0].strip():  # type: ignore[index]
                                # Skip header rows
                                if any(h in str(row[0]).lower() for h in ["sr", "serial", "s.no", "#"]):  # type: ignore[index]
                                    continue

                                entry = CauseListEntry(
                                    serial_number=serial,
                                    case_number=str(row[1] or "").strip() if len(row) > 1 else "",  # type: ignore[index]
                                    petitioner=str(row[2] or "").strip() if len(row) > 2 else "",  # type: ignore[index]
                                    respondent=str(row[3] or "").strip() if len(row) > 3 else "",  # type: ignore[index]
                                    advocate_petitioner=str(row[4] or "").strip() if len(row) > 4 else None,  # type: ignore[index]
                                    listing_date=target_date,
                                )
                                if entry.case_number:
                                    entries.append(entry)  # type: ignore[attr-defined]
                                    serial += 1  # type: ignore[operator]

            if entries:
                return [CauseList(
                    court_name=court_name,
                    list_date=target_date,
                    total_cases=len(entries),
                    entries=entries,
                )]
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")

        return []

    def _find_pdf_links(self, soup: BeautifulSoup, target_date: date) -> List[str]:
        """Find PDF download links for cause lists."""
        pdf_links = []
        date_str = target_date.strftime("%d")

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)

            if href.lower().endswith(".pdf"):
                if date_str in text or target_date.strftime("%d-%m") in href:
                    pdf_links.append(href)

        return pdf_links

    async def _download_and_parse_pdf(
        self, pdf_url: str, court_name: str, target_date: date
    ) -> List:
        """Download and parse a PDF cause list."""
        try:
            async with httpx.AsyncClient(timeout=30, headers=self.headers) as client:
                response = await client.get(pdf_url)
                if response.status_code == 200:
                    return await self._parse_pdf_causelist(
                        response.content, court_name, target_date
                    )
        except Exception as e:
            logger.error(f"PDF download failed: {e}")
        return []

    async def find_case_in_causelist(
        self, court_name: str, case_number: str,
        date_from: date, date_to: date
    ) -> List[Dict]:
        """Search for a case in cause lists across a date range."""
        results = []
        current = date_from
        while current <= date_to:
            if current.weekday() < 5:  # Skip weekends
                cause_lists = await self.scrape_causelist(court_name, current)
                for cl in cause_lists:
                    for entry in cl.entries:
                        if case_number.upper() in entry.case_number.upper():
                            results.append({
                                "date": current.isoformat(),  # type: ignore[attr-defined]
                                "court_number": cl.court_number,
                                "bench": cl.bench,
                                "entry": entry.model_dump(mode="json"),
                            })
            current = current.replace(day=current.day + 1) if current.day < 28 else date(
                current.year + (current.month // 12),
                (current.month % 12) + 1,
                1,
            )
        return results
