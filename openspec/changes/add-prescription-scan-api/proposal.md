# Change: Add Prescription Scan API with Groq Vision

## Why
The MediScan app needs an AI-powered endpoint to extract medicine names from prescription images. Using Groq's free LLaMA 3.2 Vision model provides a cost-effective solution with fast inference times.

## What Changes
- Add new POST endpoint `/scan` that accepts prescription images via multipart form upload
- Integrate Groq API client for vision model inference (llama-3.2-90b-vision-preview)
- Return JSON response with extracted medicine names
- Add environment variable configuration for Groq API key

## Impact
- Affected specs: `prescription-scan` (new capability)
- Affected code: `src/mediscan_ai/main.py`, `requirements.txt`
- New dependency: `groq` Python SDK

