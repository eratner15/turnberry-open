"""Anti-hallucination validation layer."""

import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

from loguru import logger

from .models import LLMResponse, Signal


class QuoteValidator:
    """Validates that LLM-extracted quotes actually exist in source documents."""

    def __init__(self, min_similarity: float = 0.85):
        """
        Initialize validator.

        Args:
            min_similarity: Minimum similarity score (0.0-1.0) for fuzzy matching
        """
        self.min_similarity = min_similarity

    def validate_response(
        self,
        llm_response: LLMResponse,
        source_text: str,
        page_texts: Optional[Dict[int, str]] = None
    ) -> Tuple[LLMResponse, List[str]]:
        """
        Validate LLM response against source document.

        Args:
            llm_response: LLM classification response
            source_text: Full source document text
            page_texts: Optional dict mapping page numbers to text

        Returns:
            (validated_response, warnings)
            validated_response: Updated response with only verified quotes
            warnings: List of validation warnings/issues found
        """
        warnings = []

        if not llm_response.has_signal or not llm_response.signals:
            return llm_response, warnings

        validated_signals = []

        for idx, signal in enumerate(llm_response.signals):
            # Validate the quote
            is_valid, page_num, similarity = self._validate_quote(
                signal.specific_quote,
                source_text,
                page_texts
            )

            if is_valid:
                validated_signals.append(signal)
                logger.info(
                    f"✓ Quote {idx + 1} verified (similarity: {similarity:.2f}, page: {page_num or 'N/A'})"
                )
            else:
                warning = (
                    f"Quote rejected (similarity: {similarity:.2f}): "
                    f'"{signal.specific_quote[:100]}..."'
                )
                warnings.append(warning)
                logger.warning(warning)

        # Update response with only validated signals
        if len(validated_signals) < len(llm_response.signals):
            removed_count = len(llm_response.signals) - len(validated_signals)
            logger.warning(f"Removed {removed_count} unverified quotes")

        # If no signals validated, mark as no signal
        if not validated_signals:
            llm_response.has_signal = False
            llm_response.confidence = 0.0
            llm_response.signals = []
            warnings.append("All quotes failed validation - marking as no signal")
        else:
            llm_response.signals = validated_signals

        return llm_response, warnings

    def _validate_quote(
        self,
        quote: str,
        source_text: str,
        page_texts: Optional[Dict[int, str]] = None
    ) -> Tuple[bool, Optional[int], float]:
        """
        Validate a single quote against source text.

        Returns:
            (is_valid, page_number, similarity_score)
        """
        # Clean the quote for matching
        quote_clean = self._clean_text(quote)

        # Try exact match first
        if quote_clean in self._clean_text(source_text):
            page_num = self._find_page_number(quote_clean, page_texts) if page_texts else None
            return True, page_num, 1.0

        # Try fuzzy match (allows for minor LLM paraphrasing or typos)
        best_similarity = 0.0
        best_page = None

        # Split source into chunks roughly the size of the quote
        chunk_size = len(quote_clean)
        source_clean = self._clean_text(source_text)

        # Sliding window search
        for i in range(0, len(source_clean) - chunk_size + 1, max(1, chunk_size // 4)):
            chunk = source_clean[i:i + chunk_size * 2]  # Allow some flexibility
            similarity = self._similarity(quote_clean, chunk)

            if similarity > best_similarity:
                best_similarity = similarity

                # If we have page texts, find which page this is on
                if page_texts and similarity >= self.min_similarity:
                    best_page = self._find_page_number(chunk, page_texts)

        is_valid = best_similarity >= self.min_similarity
        return is_valid, best_page, best_similarity

    def _find_page_number(self, text: str, page_texts: Dict[int, str]) -> Optional[int]:
        """Find which page a text snippet appears on."""
        text_clean = self._clean_text(text)

        for page_num, page_text in page_texts.items():
            if text_clean in self._clean_text(page_text):
                return page_num

        # Fuzzy match fallback
        best_page = None
        best_similarity = 0.0

        for page_num, page_text in page_texts.items():
            similarity = self._similarity(text_clean, self._clean_text(page_text[:len(text) * 3]))
            if similarity > best_similarity and similarity >= 0.7:
                best_similarity = similarity
                best_page = page_num

        return best_page

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean text for comparison (lowercase, remove extra whitespace)."""
        # Lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove punctuation that might vary (quotes, apostrophes)
        text = re.sub(r'["\'\u201c\u201d\u2018\u2019]', '', text)
        return text.strip()

    @staticmethod
    def _similarity(str1: str, str2: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher."""
        return SequenceMatcher(None, str1, str2).ratio()


class FactChecker:
    """Additional fact-checking for extracted information."""

    @staticmethod
    def validate_dollar_amount(amount_str: Optional[str], source_text: str) -> bool:
        """Verify that a dollar amount actually appears in the source."""
        if not amount_str:
            return True  # No claim made

        # Extract numbers from the amount string
        numbers = re.findall(r'[\d,]+', amount_str)
        if not numbers:
            return True

        # Check if any of these numbers appear in the source
        source_clean = source_text.lower()
        for num in numbers:
            num_clean = num.replace(',', '')
            if num_clean in source_clean or num in source_clean:
                return True

        logger.warning(f"Dollar amount not verified in source: {amount_str}")
        return False

    @staticmethod
    def validate_contact_person(contact: Optional[str], source_text: str) -> bool:
        """Verify that a contact person's name appears in the source."""
        if not contact:
            return True  # No claim made

        # Extract potential name
        # Format might be "John Doe, Chief" or just "John Doe"
        name_match = re.match(r'^([A-Z][a-z]+ [A-Z][a-z]+)', contact)
        if not name_match:
            return True  # Can't extract name to validate

        name = name_match.group(1)
        source_clean = source_text.lower()

        if name.lower() in source_clean:
            return True

        logger.warning(f"Contact person not verified in source: {contact}")
        return False
