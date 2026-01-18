"""PDF text extraction and metadata parsing."""

import re
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime

import fitz  # PyMuPDF
from loguru import logger

from .models import DocumentMetadata


class PDFProcessor:
    """Handles PDF text extraction and metadata parsing."""

    def __init__(self):
        pass

    def process_pdf(self, pdf_path: Path) -> Tuple[str, DocumentMetadata, int, Dict[int, str]]:
        """
        Extract text and metadata from a PDF.

        Returns:
            (raw_text, metadata, page_count, page_texts)
            page_texts: Dict mapping page number (1-indexed) to text content
        """
        logger.info(f"Processing PDF: {pdf_path.name}")

        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)

            # Extract all text with page tracking
            raw_text = ""
            page_texts = {}

            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                page_texts[page_num + 1] = page_text  # 1-indexed for human readability
                raw_text += page_text

            doc.close()

            # Parse metadata
            metadata = self._parse_metadata(pdf_path, raw_text)

            logger.info(f"Extracted {len(raw_text)} chars from {page_count} pages")
            return raw_text, metadata, page_count, page_texts

        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            raise

    def _parse_metadata(self, pdf_path: Path, text: str) -> DocumentMetadata:
        """Parse metadata from filename and content."""

        filename = pdf_path.name
        municipality_name = self._extract_municipality(filename, text)
        meeting_date = self._extract_meeting_date(filename, text)
        meeting_type = self._extract_meeting_type(filename, text)

        return DocumentMetadata(
            filename=filename,
            municipality_name=municipality_name,
            state="TX",  # Default to Texas for now
            meeting_date=meeting_date,
            meeting_type=meeting_type,
        )

    def _extract_municipality(self, filename: str, text: str) -> Optional[str]:
        """Extract municipality name from filename or content."""

        # Try filename first (common patterns)
        # Examples: "Austin_Council_Minutes_2024.pdf", "City of Dallas - Jan 2024.pdf"
        texas_cities = [
            "Austin", "Dallas", "Houston", "San Antonio", "Fort Worth",
            "El Paso", "Arlington", "Corpus Christi", "Plano", "Laredo",
            "Lubbock", "Garland", "Irving", "Amarillo", "Grand Prairie",
        ]

        # Check filename
        filename_lower = filename.lower()
        for city in texas_cities:
            if city.lower() in filename_lower:
                return city

        # Check first 1000 chars of text
        text_sample = text[:1000].lower()
        for city in texas_cities:
            if city.lower() in text_sample:
                return city

        # Try to find "City of X" pattern
        city_pattern = r'city of ([a-z\s]+)'
        match = re.search(city_pattern, text_sample, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

        return None

    def _extract_meeting_date(self, filename: str, text: str) -> Optional[str]:
        """Extract meeting date in YYYY-MM-DD format."""

        # Common date patterns in filenames and text
        # Examples: "2024-01-15", "01/15/2024", "January 15, 2024"

        # Pattern 1: YYYY-MM-DD or YYYY_MM_DD
        pattern1 = r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})'
        match = re.search(pattern1, filename)
        if match:
            year, month, day = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Pattern 2: MM/DD/YYYY or MM-DD-YYYY
        pattern2 = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.search(pattern2, filename)
        if match:
            month, day, year = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Pattern 3: "January 15, 2024" in text
        text_sample = text[:2000]
        pattern3 = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})'
        match = re.search(pattern3, text_sample, re.IGNORECASE)
        if match:
            month_name, day, year = match.groups()
            try:
                date_obj = datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None

    def _extract_meeting_type(self, filename: str, text: str) -> str:
        """Extract meeting type (council, planning, etc.)."""

        filename_lower = filename.lower()
        text_sample = text[:1000].lower()

        meeting_types = {
            "council": ["council", "city council"],
            "planning": ["planning", "planning commission"],
            "public_works": ["public works"],
            "budget": ["budget"],
            "public_safety": ["public safety"],
        }

        # Check filename first
        for meeting_type, keywords in meeting_types.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    return meeting_type

        # Check text
        for meeting_type, keywords in meeting_types.items():
            for keyword in keywords:
                if keyword in text_sample:
                    return meeting_type

        return "council"  # Default
