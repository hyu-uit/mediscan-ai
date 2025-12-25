"""Tests for main module."""

import io
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from mediscan_ai.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to MediScan AI"}


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_scan_without_file():
    """Test scan endpoint without file."""
    response = client.post("/scan")
    assert response.status_code == 422  # Validation error


def test_scan_with_file_no_groq_client():
    """Test scan endpoint when Groq client is not configured."""
    dummy_image = io.BytesIO(b"fake image content")

    with patch("mediscan_ai.services._groq_client", None):
        response = client.post(
            "/scan",
            files={"file": ("test.jpg", dummy_image, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "cant read the document"


def test_scan_success():
    """Test scan endpoint with successful medication extraction."""
    dummy_image = io.BytesIO(b"fake image content")

    mock_ai_response = """{
        "medications": [
            {
                "name": "Amoxicillin",
                "dosage": "500",
                "unit": "mg",
                "frequencyType": "daily",
                "intakeTimes": [
                    {"time": "08:00 AM", "type": "morning"},
                    {"time": "08:00 PM", "type": "night"}
                ]
            }
        ],
        "confidence": 0.9
    }"""

    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content=mock_ai_response))]

    with patch("mediscan_ai.services._groq_client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = client.post(
            "/scan",
            files={"file": ("prescription.jpg", dummy_image, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["medications"]) == 1
        assert data["medications"][0]["name"] == "Amoxicillin"
        assert data["medications"][0]["dosage"] == "500"
        assert data["medications"][0]["unit"] == "mg"
        assert data["confidence"] == 0.9


def test_scan_no_medications_found():
    """Test scan endpoint when no medications are found."""
    dummy_image = io.BytesIO(b"fake image content")

    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(message=AsyncMock(content='{"medications": [], "confidence": 0}'))
    ]

    with patch("mediscan_ai.services._groq_client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        response = client.post(
            "/scan",
            files={"file": ("prescription.jpg", dummy_image, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "cant read the document"


def test_scan_api_error():
    """Test scan endpoint when API throws an error."""
    dummy_image = io.BytesIO(b"fake image content")

    with patch("mediscan_ai.services._groq_client") as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        response = client.post(
            "/scan",
            files={"file": ("prescription.jpg", dummy_image, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "cant read the document"
