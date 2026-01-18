"""LLM-based signal classification."""

import json
from typing import Optional, Dict, Any

import llm
from loguru import logger
from pydantic import ValidationError

from .models import LLMResponse
from .prompts import get_prompt_for_vertical


class SignalClassifier:
    """Uses LLM to classify documents and extract signals."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize classifier.

        Args:
            model_name: LLM model to use (default: gpt-4o-mini for cost efficiency)
        """
        self.model_name = model_name
        self.model = llm.get_model(model_name)
        logger.info(f"Initialized classifier with model: {model_name}")

    def classify(self, text: str, vertical: str, metadata: Optional[Dict[str, Any]] = None) -> LLMResponse:
        """
        Classify document text and extract signals.

        Args:
            text: Raw document text
            vertical: Vertical to analyze for (e.g., "police-tech")
            metadata: Optional metadata to help with classification

        Returns:
            LLMResponse with signals if found
        """
        logger.info(f"Classifying document for vertical: {vertical}")

        # Get the system prompt for this vertical
        system_prompt = get_prompt_for_vertical(vertical)

        # Prepare user message with context
        user_message = self._prepare_user_message(text, metadata)

        try:
            # Call LLM
            response = self.model.prompt(
                user_message,
                system=system_prompt,
            )

            response_text = response.text().strip()
            logger.debug(f"LLM response: {response_text[:200]}...")

            # Parse JSON response
            llm_response = self._parse_llm_response(response_text)

            logger.info(
                f"Classification complete - Signal: {llm_response.has_signal}, "
                f"Confidence: {llm_response.confidence:.2f}, "
                f"Signals found: {len(llm_response.signals)}"
            )

            return llm_response

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise

    def _prepare_user_message(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Prepare the user message with text and optional metadata."""

        # Truncate text if too long (keep first 20k chars to stay within context limits)
        # Most meeting minutes are shorter, but some PDFs can be huge
        max_chars = 20000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Document truncated for length]"
            logger.warning(f"Document truncated to {max_chars} chars")

        message = "Analyze the following municipal meeting document:\n\n"

        if metadata:
            message += "METADATA:\n"
            if metadata.get("municipality_name"):
                message += f"Municipality: {metadata['municipality_name']}\n"
            if metadata.get("meeting_date"):
                message += f"Meeting Date: {metadata['meeting_date']}\n"
            if metadata.get("meeting_type"):
                message += f"Meeting Type: {metadata['meeting_type']}\n"
            message += "\n"

        message += "DOCUMENT TEXT:\n"
        message += text

        return message

    def _parse_llm_response(self, response_text: str) -> LLMResponse:
        """Parse and validate LLM JSON response."""

        # Clean up response (sometimes LLMs wrap JSON in markdown code blocks)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

        try:
            return LLMResponse(**response_data)
        except ValidationError as e:
            logger.error(f"Response validation failed: {e}")
            logger.error(f"Response data: {response_data}")
            raise ValueError(f"LLM response failed validation: {e}")
