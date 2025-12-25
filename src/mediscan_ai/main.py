"""Main entry point for MediScan AI service."""

import logging

from fastapi import FastAPI, File, UploadFile

from mediscan_ai.models import (
    HealthResponse,
    ScanErrorResponse,
    ScanResponse,
    ScanSuccessResponse,
)
from mediscan_ai.services import extract_medicines_from_image, get_groq_client

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
    """Scan a prescription image and extract medicine names."""
    if not get_groq_client():
        logger.error("Groq client not initialized - check GROQ_API_KEY")
        return ScanErrorResponse(error="cant read the document")

    try:
        image_bytes = await file.read()
        logger.info(f"Processing image: {file.filename}, size: {len(image_bytes)} bytes")
        
        medicines = await extract_medicines_from_image(image_bytes, file.content_type)
        logger.info(f"Extracted medicines: {medicines}")

        if not medicines:
            return ScanErrorResponse(error="cant read the document")

        return ScanSuccessResponse(medicines=medicines)

    except Exception as e:
        logger.error(f"Error scanning prescription: {type(e).__name__}: {e}")
        return ScanErrorResponse(error="cant read the document")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=2332)
