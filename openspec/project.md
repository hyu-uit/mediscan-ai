# Project Context

## Purpose
MediScan Reminder is a mobile application that helps patients take their medications on time. The app scans doctor's prescriptions using OCR and AI, extracts medicine names, dosage, and schedules, automatically creates medicine intake schedules, sends push notifications at scheduled times, and escalates reminders via automated phone calls if the user does not confirm taking the medicine.

### Target Users
- Patients with chronic conditions
- Elderly users (60+) who need frequent reminders and prefer phone calls
- Caregivers managing medication for others
- Busy professionals who need strict reminders

### Success Metrics
- % of prescriptions successfully scanned
- % of reminders confirmed as taken
- Reduction in missed-dose rate
- Daily/Monthly Active Users (DAU/MAU)
- Retention rate (7-day, 30-day)

## Tech Stack

### Mobile Application
- React Native (TypeScript)
- Expo framework
- expo-camera / react-native-vision-camera
- Firebase Cloud Messaging (Android) + APNs (iOS)
- Local notifications (offline fallback)
- Secure Storage (Keychain / Keystore)

### Backend API
- Node.js + Express.js
- Prisma ORM
- PostgreSQL
- Redis (job queue for reminders)
- BullMQ / Agenda (scheduling)
- JWT authentication

### AI OCR & NLP Service
- Python (FastAPI)
- Google Vision API / AWS Textract (primary OCR)
- Tesseract (fallback OCR)
- spaCy + custom rule-based parser

### Infrastructure
- Dockerized services
- AWS / GCP / Azure hosting
- Managed PostgreSQL (RDS / Neon)

## Project Conventions

### Code Style
- TypeScript for all React Native code
- Python for AI/OCR service
- ESLint + Prettier for JavaScript/TypeScript
- Simple, accessible language in UI
- Large text and buttons for elderly accessibility
- Localization-ready architecture

### Architecture Patterns
- **Mobile**: Feature-based module structure
- **Backend**: Service-oriented architecture
  - Auth Service
  - Prescription Service
  - Reminder Scheduler Service
  - Notification Service
  - Call Escalation Service
- **Database**: Soft deletes for medical data, audit logging, timezone-aware timestamps
- **API**: RESTful with structured JSON responses

### Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- OCR accuracy testing with sample prescriptions
- End-to-end testing for critical user flows (scan → schedule → reminder → confirmation)

### Git Workflow
- Feature branches from main
- Pull requests with code review
- Conventional commits for changelog generation

## Domain Context

### Core User Journey
1. User installs app and grants permissions (camera, notifications, calls)
2. Sets default intake times (morning, noon, afternoon, night, before sleep)
3. Scans prescription via camera or upload
4. App extracts and confirms medicine schedule (editable)
5. Push notification sent at intake time
6. User marks medicine as "Taken" or "Skip"
7. If no action after 5 minutes → automated call triggered
8. History saved for tracking and adherence analytics

### Medical Entity Recognition
- Medicine name
- Dosage
- Frequency (X times/day, specific times, before/after meals)
- Timing instructions
- Duration (start date, end date)

### Escalation Logic
- Push notification first
- Wait 5 minutes for user interaction
- If no response → trigger automated voice call
- Optional repeat call (configurable)

## Important Constraints

### Technical Constraints
- OCR accuracy depends on prescription handwriting quality
- OCR response must be < 3 seconds
- Notification delivery < 5 seconds delay
- 99.9% uptime target
- Offline reminder fallback required

### Regulatory Constraints
- Medical regulations vary by region
- HIPAA/GDPR-ready architecture required
- Medical disclaimer: App does not replace doctor advice
- User consent required for calls and data usage
- No prescription sharing without consent

### Business Constraints
- Automated calls depend on telecom/VoIP provider limitations
- Users must allow notification and call permissions
- Internet required for OCR processing

## External Dependencies

### OCR & AI
- **Primary**: Google Vision API or AWS Textract
- **Fallback**: Tesseract OCR

### Push Notifications
- Firebase Cloud Messaging (Android)
- Apple Push Notification Service (iOS)

### Automated Calls
- Twilio / Agora / Vonage (VoIP providers)
- Text-to-speech for call reminders

### Database
- PostgreSQL (managed via RDS / Neon)
- Redis (job queue)

## Database Schema (Core Tables)
- `users` - User accounts and preferences
- `prescriptions` - Scanned prescription records
- `medicines` - Extracted medicine data
- `medicine_schedules` - Generated reminder schedules
- `reminder_logs` - Notification and confirmation history
- `call_logs` - Escalation call records
- `user_default_times` - Default intake time preferences

## Future Enhancements (v2+)
- Caregiver & multi-user support with dependent profiles
- AI dosage validation
- Smartwatch integration
- Voice input
- Pharmacy integration
- Refill reminders
