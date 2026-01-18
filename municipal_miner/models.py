"""Pydantic models for data validation."""

from typing import Optional, List
from pydantic import BaseModel, Field


class Signal(BaseModel):
    """Represents a single procurement signal."""

    type: str = Field(..., description="Signal type: budget_approval, vendor_dissatisfaction, pilot_program, needs_discussion")
    specific_quote: str = Field(..., max_length=200, description="Direct quote from document")
    context: str = Field(..., description="2-3 sentence summary")
    contact_person: Optional[str] = Field(None, description="Name and title if mentioned")
    estimated_value: Optional[str] = Field(None, description="Dollar amount if mentioned")
    urgency: str = Field(..., description="low, medium, or high")
    next_action: str = Field(..., description="What municipality plans to do next")


class LLMResponse(BaseModel):
    """Response from LLM classification."""

    has_signal: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    municipality: Optional[str] = None
    state: Optional[str] = None
    meeting_date: Optional[str] = None
    signals: List[Signal] = Field(default_factory=list)
    reason: Optional[str] = Field(None, description="Explanation if no signal found")


class DocumentMetadata(BaseModel):
    """Metadata parsed from document."""

    filename: str
    municipality_name: Optional[str] = None
    state: str = "TX"  # Default to Texas
    meeting_date: Optional[str] = None
    meeting_type: Optional[str] = "council"
