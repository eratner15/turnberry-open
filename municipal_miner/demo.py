"""Demo mode for testing without API calls."""

from typing import Dict, Any, Optional
from .models import LLMResponse, Signal


class DemoClassifier:
    """Demo classifier that returns pre-defined signals for testing."""

    def __init__(self, model_name: str = "demo"):
        self.model_name = model_name

    def classify(self, text: str, vertical: str, metadata: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """Return demo signals based on text content."""

        # Check if text contains police-tech keywords
        text_lower = text.lower()

        signals = []
        confidence = 0.0

        # Look for body camera signals
        if "body camera" in text_lower or "body-worn camera" in text_lower:
            # Extract actual quote from text
            quote = self._extract_quote(text, ["body camera", "body-worn camera", "bwc"])
            if quote:
                signals.append(Signal(
                    type="vendor_dissatisfaction",
                    specific_quote=quote[:200],
                    context="The police department raised concerns about current body camera system costs and reliability during the budget review meeting. This indicates potential vendor switching or contract renegotiation.",
                    contact_person=self._extract_contact(text),
                    estimated_value=self._extract_dollar_amount(text),
                    urgency="high",
                    next_action="Contract renewal decision expected within 60 days"
                ))
                confidence = 0.89

        # Look for evidence management signals
        if "evidence" in text_lower and ("storage" in text_lower or "management" in text_lower):
            quote = self._extract_quote(text, ["evidence storage", "evidence management", "digital evidence"])
            if quote:
                signals.append(Signal(
                    type="needs_discussion",
                    specific_quote=quote[:200],
                    context="Discussion of evidence storage and management challenges suggests upcoming procurement for digital evidence management solutions.",
                    contact_person=None,
                    estimated_value=None,
                    urgency="medium",
                    next_action="Further discussion scheduled for next committee meeting"
                ))
                confidence = max(confidence, 0.76)

        # Look for budget approval signals
        if "budget" in text_lower and ("approve" in text_lower or "allocation" in text_lower):
            quote = self._extract_quote(text, ["budget", "allocation", "approve"])
            if quote:
                signals.append(Signal(
                    type="budget_approval",
                    specific_quote=quote[:200],
                    context="Budget allocation approved for public safety technology upgrades, indicating imminent procurement activity.",
                    contact_person=self._extract_contact(text),
                    estimated_value=self._extract_dollar_amount(text),
                    urgency="high",
                    next_action="RFP expected to be published within 30-45 days"
                ))
                confidence = 0.92

        if not signals:
            return LLMResponse(
                has_signal=False,
                confidence=0.0,
                reason="No police technology procurement signals detected in document"
            )

        # Extract municipality info from metadata
        municipality = None
        state = "TX"
        meeting_date = None

        if metadata:
            municipality = metadata.get("municipality_name")
            state = metadata.get("state", "TX")
            meeting_date = metadata.get("meeting_date")

        return LLMResponse(
            has_signal=True,
            confidence=confidence,
            municipality=municipality,
            state=state,
            meeting_date=meeting_date,
            signals=signals
        )

    def _extract_quote(self, text: str, keywords: list) -> Optional[str]:
        """Extract a sentence containing keywords."""
        sentences = text.split('.')
        for sentence in sentences:
            for keyword in keywords:
                if keyword.lower() in sentence.lower():
                    return sentence.strip()
        return None

    def _extract_contact(self, text: str) -> Optional[str]:
        """Extract contact person if mentioned."""
        import re
        # Look for Chief/Commander/Captain followed by name
        patterns = [
            r'(Chief|Commander|Captain|Director)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(Chief|Commander|Captain|Director)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if 'Chief' in match.group(0) or 'Commander' in match.group(0):
                    return match.group(0)
        return None

    def _extract_dollar_amount(self, text: str) -> Optional[str]:
        """Extract dollar amounts from text."""
        import re
        # Look for dollar amounts like $XXX,XXX or $XXXk
        pattern = r'\$[\d,]+[kKmM]?'
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        return None
