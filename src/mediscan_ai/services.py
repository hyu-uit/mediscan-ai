"""AI services for prescription scanning."""

from __future__ import annotations

import base64
import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Initialize Groq client
_groq_client: Optional[Groq] = None
_GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if _GROQ_API_KEY:
    _groq_client = Groq(api_key=_GROQ_API_KEY)


def get_groq_client() -> Optional[Groq]:
    """Get the Groq client instance."""
    return _groq_client


def _image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def _get_image_media_type(content_type: Optional[str]) -> str:
    """Get media type for the image."""
    if content_type and content_type.startswith("image/"):
        return content_type
    return "image/jpeg"


def _generate_id() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def _parse_medications_from_response(result_text: str) -> Dict[str, Any]:
    """Parse medication details from AI response."""
    try:
        # Try to find JSON object in response
        if result_text.startswith("{"):
            return json.loads(result_text)
        else:
            # Try to extract JSON from markdown code blocks or text
            match = re.search(r"\{[\s\S]*\}", result_text)
            if match:
                return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return {"medications": []}


def _ensure_ids(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all medications and intake times have IDs."""
    medications = data.get("medications", [])
    for med in medications:
        if not med.get("id"):
            med["id"] = _generate_id()
        intake_times = med.get("intakeTimes", [])
        if intake_times:
            for intake in intake_times:
                if not intake.get("id"):
                    intake["id"] = _generate_id()
    return data


EXTRACTION_PROMPT = """Analyze this prescription image and extract all medication details.

Return a JSON object with this EXACT structure:
{
  "medications": [
    {
      "name": "Medicine Name",
      "dosage": "500",
      "unit": "mg",
      "instructions": "Take with food",
      "notes": "Any additional notes",
      "frequencyType": "daily",
      "intervalValue": "1",
      "intervalUnit": "days",
      "selectedDays": ["monday", "wednesday", "friday"],
      "intakeTimes": [
        {"time": "08:00 AM", "type": "morning"},
        {"time": "08:00 PM", "type": "night"}
      ]
    }
  ],
  "rawText": "Raw text from prescription if readable",
  "confidence": 0.85
}

IMPORTANT RULES:
1. Extract ALL medications found in the prescription
2. Use these EXACT values for fields:
   - unit: "mg", "ml", "tablet", "capsule", "drop", "patch"
   - frequencyType: "daily", "interval", "specific_days"
   - intervalUnit: "days", "weeks", "months"
   - type (for intakeTimes): "morning", "noon", "afternoon", "night", "before_sleep"
   - selectedDays: "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"
3. If information is not available, omit the field (don't use null)
4. For time, use 12-hour format like "08:00 AM", "02:00 PM"
5. confidence should be 0-1 based on image clarity and readability
6. Return ONLY the JSON object, no other text

If you cannot read the prescription, return: {"medications": [], "confidence": 0}"""


async def extract_medications_from_image(
    image_bytes: bytes, content_type: Optional[str]
) -> Dict[str, Any]:
    """Extract medication details from prescription image using Groq Vision.

    Args:
        image_bytes: Raw image bytes
        content_type: MIME type of the image

    Returns:
        Dictionary with medications list and metadata

    Raises:
        ValueError: If Groq client is not initialized
    """
    if not _groq_client:
        raise ValueError("Groq client not initialized")

    base64_image = _image_to_base64(image_bytes)
    media_type = _get_image_media_type(content_type)

    response = _groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    result_text = response.choices[0].message.content.strip()
    data = _parse_medications_from_response(result_text)
    return _ensure_ids(data)
