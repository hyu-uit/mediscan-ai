## Context
MediScan AI needs to extract medication information from prescription images. This is the first AI feature for the service, requiring integration with an external AI provider.

## Goals / Non-Goals
- **Goals:**
  - Accept prescription images via file upload
  - Extract medicine names using Groq's vision model
  - Return structured JSON response
  - Provide clear error messages for unreadable documents

- **Non-Goals:**
  - Extract dosage, frequency, or timing (future enhancement)
  - Support multiple image formats beyond common types (jpg, png)
  - Implement caching or rate limiting (can be added later)

## Decisions

### Decision: Use Groq as AI Provider
- **Why:** Free tier available, fast inference (~10x faster than alternatives), simple API
- **Model:** `llama-3.2-90b-vision-preview` - best accuracy for vision tasks
- **Alternatives considered:**
  - Google Vision API: More accurate for OCR but costs money
  - OpenAI GPT-4 Vision: Expensive, slower
  - Local Tesseract: Free but poor accuracy for handwritten text

### Decision: Multipart Form Upload for Images
- **Why:** Standard approach, works well with Postman/curl, handles binary data efficiently
- **Alternatives considered:**
  - Base64 in JSON body: Larger payload size, more complex client code

### Decision: Simple Error Response
- **Why:** User requested simple "cant read the document" message for failures
- **Future:** Can add confidence scores and partial results later

## Risks / Trade-offs
- **Risk:** Groq API rate limits on free tier → Mitigation: Document limits, can upgrade later
- **Risk:** Model accuracy varies with handwriting quality → Mitigation: Clear error message for failures
- **Trade-off:** Using vision LLM instead of dedicated OCR - less accurate for pure text, but better at understanding context

## API Design

### Request
```
POST /scan
Content-Type: multipart/form-data

file: <prescription_image>
```

### Success Response (200)
```json
{
  "success": true,
  "medicines": ["Amoxicillin", "Ibuprofen"]
}
```

### Failure Response (422)
```json
{
  "success": false,
  "error": "cant read the document"
}
```

## Environment Variables
- `GROQ_API_KEY`: Required API key from Groq console (https://console.groq.com)

