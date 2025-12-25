"""Pydantic models for MediScan AI service."""

from typing import List, Union

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str


class ScanSuccessResponse(BaseModel):
    """Successful scan response with extracted medicines."""

    success: bool = True
    medicines: List[str]


class ScanErrorResponse(BaseModel):
    """Error response when scan fails."""

    success: bool = False
    error: str


ScanResponse = Union[ScanSuccessResponse, ScanErrorResponse]

