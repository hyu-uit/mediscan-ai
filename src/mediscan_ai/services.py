"""AI services for prescription scanning."""

from __future__ import annotations

import base64
import json
import os
import re
from typing import List, Optional

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from groq import Groq  # pyright: ignore[reportMissingImports]

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


def _parse_medicines_from_response(result_text: str) -> List[str]:
    """Parse medicine names from AI response."""
    try:
        if result_text.startswith("["):
            medicines = json.loads(result_text)
        else:
            match = re.search(r"\[.*?\]", result_text, re.DOTALL)
            if match:
                medicines = json.loads(match.group())
            else:
                medicines = []
    except json.JSONDecodeError:
        medicines = []

    return medicines if isinstance(medicines, list) else []


async def extract_medicines_from_image(
    image_bytes: bytes, content_type: Optional[str]
) -> List[str]:
    """Extract medicine names from prescription image using Groq Vision.

    Args:
        image_bytes: Raw image bytes
        content_type: MIME type of the image

    Returns:
        List of medicine names extracted from the prescription

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
                        "text": """Analyze this prescription image and extract all medicine names.
Return ONLY a JSON array of medicine names, nothing else.
Example: ["Amoxicillin", "Ibuprofen", "Paracetamol"]
If you cannot read the prescription or find no medicines, return an empty array: []""",
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
        max_tokens=500,
    )

    result_text = response.choices[0].message.content.strip()
    return _parse_medicines_from_response(result_text)

