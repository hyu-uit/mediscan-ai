## ADDED Requirements

### Requirement: Prescription Image Upload
The system SHALL accept prescription images via multipart form-data file upload at the `/scan` endpoint.

#### Scenario: Valid image upload
- **WHEN** a user uploads a valid image file (JPEG, PNG) to POST `/scan`
- **THEN** the system accepts the file and processes it

#### Scenario: Missing file
- **WHEN** a user sends a request to POST `/scan` without a file
- **THEN** the system returns HTTP 422 with validation error

### Requirement: Medicine Name Extraction
The system SHALL extract medicine names from the uploaded prescription image using Groq's LLaMA 3.2 Vision model.

#### Scenario: Readable prescription
- **WHEN** a readable prescription image is uploaded
- **THEN** the system returns a JSON response with `success: true` and a `medicines` array containing extracted medicine names

#### Scenario: Unreadable prescription
- **WHEN** the prescription image cannot be read or no medicines are detected
- **THEN** the system returns a JSON response with `success: false` and `error: "cant read the document"`

### Requirement: Groq API Configuration
The system SHALL read the Groq API key from the `GROQ_API_KEY` environment variable.

#### Scenario: API key configured
- **WHEN** the `GROQ_API_KEY` environment variable is set
- **THEN** the system uses this key to authenticate with Groq API

#### Scenario: API key missing
- **WHEN** the `GROQ_API_KEY` environment variable is not set
- **THEN** the system logs an error and the `/scan` endpoint returns HTTP 500

