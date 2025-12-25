"""Main entry point for MediScan AI service."""

import logging

from fastapi import FastAPI, File, UploadFile

from mediscan_ai.models import (
    HealthResponse,
    IntakeTime,
    Medication,
    ScanErrorResponse,
    ScanResponse,
    ScanSuccessResponse,
)
from mediscan_ai.services import extract_medications_from_image, get_groq_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MediScan AI",
    description="AI-powered medication analysis service",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to MediScan AI"}


@app.post("/scan", response_model=ScanResponse)
async def scan_prescription(file: UploadFile = File(...)) -> ScanResponse:
    """Scan a prescription image and extract medication details."""
    if not get_groq_client():
        logger.error("Groq client not initialized - check GROQ_API_KEY")
        return ScanErrorResponse(error="cant read the document")

    try:
        image_bytes = await file.read()
        logger.info(f"Processing image: {file.filename}, size: {len(image_bytes)} bytes")

        result = await extract_medications_from_image(image_bytes, file.content_type)
        logger.info(f"Extracted {len(result.get('medications', []))} medications")

        medications_data = result.get("medications", [])
        if not medications_data:
            return ScanErrorResponse(error="cant read the document")

        # Convert to Pydantic models
        medications = []
        for med_data in medications_data:
            intake_times = None
            if med_data.get("intakeTimes"):
                intake_times = [
                    IntakeTime(
                        id=it.get("id", ""),
                        time=it.get("time", ""),
                        type=it.get("type", ""),
                    )
                    for it in med_data["intakeTimes"]
                ]

            medications.append(
                Medication(
                    id=med_data.get("id", ""),
                    name=med_data.get("name", ""),
                    dosage=med_data.get("dosage"),
                    unit=med_data.get("unit"),
                    instructions=med_data.get("instructions"),
                    notes=med_data.get("notes"),
                    frequencyType=med_data.get("frequencyType"),
                    intervalValue=med_data.get("intervalValue"),
                    intervalUnit=med_data.get("intervalUnit"),
                    selectedDays=med_data.get("selectedDays"),
                    intakeTimes=intake_times,
                )
            )

        return ScanSuccessResponse(
            medications=medications,
            rawText=result.get("rawText"),
            confidence=result.get("confidence"),
        )

    except Exception as e:
        logger.error(f"Error scanning prescription: {type(e).__name__}: {e}")
        return ScanErrorResponse(error="cant read the document")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=2332)
