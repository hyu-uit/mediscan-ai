"""Pydantic models for MediScan AI service."""

from typing import List, Optional, Union

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str


class IntakeTime(BaseModel):
    """Intake time slot for medication."""

    id: str
    time: str  # "08:00 AM", "02:00 PM"
    type: str  # "morning", "noon", "afternoon", "night", "before_sleep"


class Medication(BaseModel):
    """Medication details extracted from prescription."""

    id: str
    name: str
    dosage: Optional[str] = None  # "500", "250"
    unit: Optional[str] = None  # "mg", "ml", "tablet", "capsule", "drop", "patch"
    instructions: Optional[str] = None  # "Take with food"
    notes: Optional[str] = None
    frequencyType: Optional[str] = None  # "daily", "interval", "specific_days"
    intervalValue: Optional[str] = None  # "1", "2", "3"
    intervalUnit: Optional[str] = None  # "days", "weeks", "months"
    selectedDays: Optional[List[str]] = None  # ["monday", "wednesday"]
    intakeTimes: Optional[List[IntakeTime]] = None


class ScanSuccessResponse(BaseModel):
    """Successful scan response with extracted medications."""

    success: bool = True
    medications: List[Medication]
    rawText: Optional[str] = None
    confidence: Optional[float] = None


class ScanErrorResponse(BaseModel):
    """Error response when scan fails."""

    success: bool = False
    error: str


ScanResponse = Union[ScanSuccessResponse, ScanErrorResponse]
