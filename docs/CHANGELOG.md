# Autoshkolla Platform Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.3] - 2026-03-14

### Messaging System Bug Fixes

#### Added
- **`PUT /conversations/{id}/read` endpoint**: Marks all unread messages in a conversation as read for the current user (excludes messages sent by the user). Includes participant authorization check.
- **4 new integration tests**: `test_mark_conversation_read`, `test_mark_conversation_read_not_found`, `test_conversation_last_message_is_object`, `test_message_to_dict_has_sender_object`

#### Fixed
- **`lastMessage` serialization**: Changed from a truncated plain string to a proper object with `{content, senderId, senderName, createdAt}` so the frontend can display sender info and timestamps in the conversation list
- **`Message.to_dict()` sender field**: Added nested `sender` object `{id, fullName, role}` so the frontend can access `message.sender.fullName` for displaying sender names in message bubbles
- **Frontend TypeScript types**: Updated `Conversation.lastMessage` type from `Message` to `LastMessagePreview`, updated `Message.sender` type to match the lightweight sender object returned by the backend, removed unused `tenantId` from `Message` type

#### Changed
- Removed unused `case` import from `sqlalchemy` in messages API
- Updated API_REFERENCE.md to mark messaging endpoints as Implemented

---

## [0.6.2] - 2026-03-14

### Comprehensive Admin Dashboard

#### Changed
- **Enhanced `GET /dashboard/stats` endpoint**: Now returns `totalCandidates`, `activeCandidates`, `archivedCandidates`, `totalRevenue`, `monthlyRevenue`, `pendingPayments`, and `recentCandidates` (last 5 registered) in addition to existing fields
- **Rebuilt dashboard frontend page**: Comprehensive layout with:
  - 4 primary stat cards: Total Candidates, Active Candidates, Total Revenue, Pending Payments
  - 3 secondary stat cards: Practical Hours Today, Instructor Debt, Archived Candidates
  - Each card has colored left border, Lucide icon, and contextual sub-text
  - 3-column grid: Category Breakdown (bar chart), Recent Candidates (clickable list with badges), Today's Schedule
  - Alerts section with color-coded severity and clickable links
- **Updated TypeScript types**: Added `RecentCandidate` interface and expanded `DashboardStats` type with all new fields

#### Fixed
- Updated API_REFERENCE.md to mark all 4 dashboard endpoints as Implemented

---

## [0.6.1] - 2026-03-10

### PDF Templates — Vertetimi & Candidate List Templates Added

#### Added
- **VËRTETIMI (Certificate) Template**: Professional government-style certificate with:
  - Kosovo coat of arms and trilingual government header (Albanian/Serbian/English)
  - Blue-tinted header (#e8f0f8) matching Fleteparaqitja design language
  - Certificate body with candidate details and completion information
  - Details table with alternating row colors showing hours, verification, medical/Red Cross certs
  - Signature section with stamp area and director/representative signature
- **CANDIDATE LIST Template**: Landscape A4 list with:
  - Dark navy (#1a2744) table header matching Fatura design language
  - 12 columns: Nr, Kodi, Emri Mbiemri, Nr. Personal, Kat., Data Regj., Instruktori, Çmimi, Paguar, Borxhi, Statusi
  - Alternating row backgrounds, right-aligned currency columns
  - Summary footer with totals for price, paid, and debt
  - Filter information display and page numbering

All 7 PDF templates now have proper inline CSS styling and parse/render correctly.

---

## [0.6.0] - 2026-03-10

### PDF Templates — ALL 5 Documents Rewritten for 100% Fidelity

#### Reference PDFs & Assets
- Downloaded 5 original PDF documents from the legacy system
- Saved to `backend/app/pdf/reference/` as ground-truth references
- Extracted image assets: school logo (school_logo_rina.png), Kosovo coat of arms (coat_of_arms_kosovo.png), 60 traffic sign images
- Created `REFERENCE_NOTES.md` with detailed layout specifications

## [Unreleased]

### PDF Templates — FATURA & KONTRATA (100% Fidelity)

#### Added
- **FATURA (Invoice) Template**: Complete rewrite with 100% fidelity to original system
  - Header section: School name, large red "FATURË" title, centered logo, invoice number and date (right-aligned)
  - Business info section: Two-column layout with school details (left) and candidate info (right, center-aligned)
  - Service table: Dark navy blue (#1a2744) header with 7 columns (Nr, Përshkrimi, Njësia, Sasia, Çmimi Pa Tvsh, TVSH, Çmimi Me Tvsh)
  - Totals section: Right-aligned with three summary rows and final "TOTALI PËR PAGESE" (bold, larger font)
  - Bank details section: Bold header "Pagesa bëhet në këtë llogari bankare" with horizontal divider
  - Signature section: Two-column layout for school and candidate signatures with descriptive text
  - All CSS inline in `<style>` tag for self-contained template
  - Supports all Jinja2 variables from `PDFGenerator.generate_fatura()`: tenant, candidate, category, invoice_number, invoice_date, price, price_no_vat, vat_amount, asset_dir
  - Uses filters: `format_date`, `format_currency`, `safe_str`

- **KONTRATA (Contract) Template**: Complete rewrite with 100% fidelity to original system
  - Title section: Centered "KONTRATË" (18pt bold) and "PËR AFTËSIMIN E KANDIDATIT PËR SHOFER" (14pt bold)
  - Date line: "E hartuar më" with underlined date in dd.MM.yyyy format
  - Opening section: School name and address (bold+underlined), candidate name and location (bold+underlined)
  - Nine numbered clauses (I-IX) with centered Roman numeral headers:
    - I: Objective (training for category)
    - II: School's obligation per Administrative Directive 13/2017
    - III: Lecturer and instructor responsibilities
    - IV: Candidate's attendance obligation
    - V: School's guarantee of adequate conditions per Directive 20/2017
    - VI: Duration, payment, and pricing (theory hours, practical hours, bank details bold+underlined)
    - VII: School license revocation procedure
    - VIII: Candidate age requirement (18+ years)
    - IX: Dispute resolution (competent court location)
  - Signature section: Two-column layout for candidate (left) and school (right) with "v.v" notation below
  - Pure text document (no tables, no images, no logos) with justified paragraph alignment
  - All CSS inline in `<style>` tag for self-contained template
  - Supports all Jinja2 variables from `PDFGenerator.generate_kontrata()`: tenant, candidate, category, candidate_residence, contract_date
  - Uses filters: `format_date`, `safe_str`, `default()`

#### Technical Details
- **File Locations**:
  - `/backend/app/pdf/templates/fatura.html` (445 lines)
  - `/backend/app/pdf/templates/kontrata.html` (271 lines)
- **Document Type**: Portrait A4 (both templates)
- **Orientation**: Portrait (both templates)
- **Character Support**: Full Albanian character support (ë, ç, etc.) via UTF-8 and Arial/Helvetica fonts
- **Integration**: Both templates fully compatible with `PDFGenerator` class and WeasyPrint engine
- **Verification**: All variables, filters, and layout elements verified against reference PDFs and REFERENCE_NOTES.md

---

## [0.7.0] - 2026-03-09

### Backend Tests — 89% Coverage (285 Tests)

#### Added
- **Test Infrastructure**: `tests/conftest.py` with session-scoped Flask app, autouse per-test DB cleanup, domain fixtures (tenants, users, categories, instructors, vehicles, candidates), JWT token helpers
- **Unit Tests** (55 tests):
  - `test_models.py` — 26 tests for all major models (Tenant, User, Category, Instructor, Vehicle, Candidate, InstructorPayment)
  - `test_services.py` — 30 tests for AuthService, CandidateService, InstructorService
  - `test_utils.py` — 14 tests for JWT utils, validation helpers, serialization
  - `test_middleware.py` — 11 tests for custom exceptions, error responses, response envelope
- **Integration Tests** (230 tests):
  - `test_auth_api.py` — 14 tests for health, login, refresh, logout, me, auth guard
  - `test_candidates_api.py` — 11 tests for candidate CRUD, search, filtering, archive
  - `test_instructors_api.py` — 11 tests for instructor CRUD, filtering, login creation
  - `test_vehicles_api.py` — 10 tests for vehicle CRUD
  - `test_categories_api.py` — 6 tests for category CRUD
  - `test_payments_api.py` — 7 tests for payment CRUD, summary
  - `test_school_users_api.py` — 10 tests for school profile, users, dashboard
  - `test_multi_tenant.py` — 7 tests for tenant data isolation
  - `test_remaining_api.py` — 45+ tests for theory hours, practical hours, expenses, instructor payments, locations, user management
  - `test_superadmin_api.py` — 18 tests for tenant CRUD, user management, impersonation, stats
  - `test_scheduled_lessons_api.py` — 12 tests for lesson CRUD, completion, cancellation
  - `test_messages_api.py` — 9 tests for conversations, messages, read/unread
  - `test_instructor_portal_api.py` — 9 tests for instructor self-service endpoints
  - `test_verifications_api.py` — 14 tests for verification CRUD
  - `test_print_docs_api.py` — 9 tests for PDF stub endpoints
- **Test Database**: `autoshkolla_platform_test` PostgreSQL database for isolated test runs

#### Fixed
- **Critical Bug**: `g.current_user['id']` → `g.current_user['sub']` in 5 API modules (`payments.py`, `users.py`, `superadmin.py`, `theory_hours.py`, `practical_hours.py`). JWT payload stores user ID as `sub`, not `id` — this caused KeyError at runtime
- **Test teardown**: Fixed `_db.drop_all()` failing on unnamed FK constraints by using raw SQL `DROP SCHEMA public CASCADE`

---

## [0.6.0] - 2026-03-09

### Database Migrations Verified & Seed Data Loaded

#### Verified
- **Alembic migration** (`bb03ba76cca2`) applied against local PostgreSQL — all 22 tables created successfully
- **76 indexes** verified (PKs, unique constraints, composite indexes for tenant-scoped queries)
- **115 constraints** verified (foreign keys, primary keys, unique constraints)
- **Schema sync confirmed** — `flask db migrate` detects no diff between models and database
- **Seed data loaded**: 2 countries (Kosovo, Albania), 38 Kosovo municipalities, 104 places, 1 demo tenant ("AutoShkolla Demo"), 2 users (admin + superadmin)

#### Database Details
- Connection: `postgresql://autoshkolla:dev_password@localhost:5432/autoshkolla_platform`
- Current Alembic head: `bb03ba76cca2`
- All UUID primary keys, tenant isolation enforced via `tenant_id` FK on all tenant-scoped tables

---

## [0.5.0] - 2026-03-09

### Full Backend Implementation — All 16 Modules

#### Added

**Phase 2 — School Management (Models, Schemas, Services, API Routes)**
- `country_model.py`, `municipality_model.py`, `place_model.py` — Shared location reference data (no tenant_id)
- `category_model.py` — Driving license categories (B, C, CE, D) with pricing and hour allocation
- `instructor_model.py` — Instructors with login capability (auto-creates User with role='instructor')
- `vehicle_model.py` — Vehicle fleet management with instructor assignment
- `seed_locations.py` — Kosovo geographic seed data (38 municipalities, 100+ places), `flask seed-locations` CLI command
- API routes: `/locations/*`, `/categories/*`, `/instructors/*`, `/vehicles/*`, `/school/profile`
- Schemas: `categories.py`, `instructors.py`, `vehicles.py`
- Services: `instructor_service.py` (auto-user creation on instructor with email+password)

**Phase 3 — Candidate Lifecycle**
- `candidate_model.py` — Core entity with 40+ columns, birth/residence locations, category, pricing, hours, document flags
- `instructor_payment_model.py` — 65€ per-candidate debt tracking, auto-created on candidate assignment
- `scheduled_lesson_model.py` — Calendar/scheduling for practical driving lessons
- `conversation_model.py`, `message_model.py` — Threaded instructor-admin messaging
- API routes: `/candidates/*`, `/scheduled-lessons/*`, `/messages/*`, `/instructor/*`, `/dashboard/*`, `/instructor-payments/*`
- Schemas: `candidates.py`, `scheduled_lessons.py`, `messages.py`
- Services: `candidate_service.py` (auto-code generation, auto-instructor-payment creation)

**Phase 4 — Theory, Practical, Payments, Verifications, Expenses, Users**
- `theory_hour_session_model.py` — Theory training sessions (1-8 sessions per candidate)
- `practical_hour_session_model.py` — Practical driving sessions with instructor and pricing
- `supplementary_registration_model.py` — Additional category registrations
- `verification_model.py` — Verification certificates with theory/practical date ranges
- `payment_model.py` — Candidate payments with auto-update of amount_paid
- `expense_type_model.py`, `expense_model.py` — Vehicle and school expense tracking
- `candidate_test_model.py` — Theory/practical test score tracking
- `audit_log_model.py` — Comprehensive audit trail with JSONB old/new values
- API routes: `/theory-hours/*`, `/practical-hours/*`, `/payments/*`, `/verifications/*`, `/expenses/*`, `/expense-types/*`, `/users/*`
- Schemas: `theory_hours.py`, `practical_hours.py`, `payments.py`, `verifications.py`, `expenses.py`, `users.py`

**Phase 5 — Super Admin & PDF Stubs**
- API routes: `/superadmin/*` (9 endpoints — tenant CRUD, user management, impersonation with JWT, global stats)
- API routes: `/print/*` (7 PDF stubs returning 501 pending WeasyPrint implementation)
- Schemas: `superadmin.py`

#### Summary
- **22 SQLAlchemy models** with UUID PKs, tenant isolation, proper indexes and relationships
- **14 Pydantic schemas** with strict validation (`extra='forbid'`)
- **3 service classes** with business logic (auth, instructor, candidate)
- **20 API route modules** with 80+ endpoints total
- **80 Python files**, all passing syntax validation
- **Seed data** for Kosovo geographic hierarchy

---

## [0.4.0] - 2026-03-09

### Instructor Portal, Calendar, Messaging & Admin Dashboard

#### Added
- **Instructor Login**: Instructors can now have email + password for login. Creating an instructor with credentials auto-creates a `users` record with `role='instructor'` linked via `instructor.user_id`
- **Instructor Portal**: Separate portal layout for instructors with dashboard, my candidates (read-only), calendar, debt tracking, and messaging
- **Instructor Debt Tracking**: 65€ per candidate charge — `instructor_payments` table tracks what each instructor owes. Auto-created when a candidate is assigned to an instructor
- **Calendar / Scheduling**: `scheduled_lessons` table for practical lesson scheduling. Supports day/week/month views, lesson completion (auto-creates `practical_hour_sessions`), cancellation with reason, and no-show tracking
- **Messaging System**: `conversations` + `messages` tables for instructor ↔ admin threaded communication. Supports read/unread tracking, conversation subjects, and participant management
- **Admin Dashboard**: Comprehensive dashboard with key metrics (active candidates, monthly revenue, today's hours, instructor debt), revenue charts, category breakdown, today's schedule, recent activity feed, and alerts for expiring documents and overdue payments
- New database tables: `instructor_payments`, `conversations`, `messages`, `scheduled_lessons`
- New columns on `instructors`: `user_id`, `email`, `cost_per_candidate`
- 30+ new API endpoints across instructor management, self-service, calendar, messaging, and dashboard modules

#### Changed
- `docs/DATABASE_SCHEMA.md` — Added 4 new tables (instructor_payments, conversations, messages, scheduled_lessons), updated instructors table with login fields
- `docs/API_REFERENCE.md` — Added sections 5b-5e for Instructor Self-Service, Calendar, Messaging, and Dashboard APIs
- `docs/MODULES_STATUS.md` — Updated Module 5 and Module 16 completion criteria
- `docs/UI_DESIGN_GUIDELINES.md` — Added sections 9b-9d for Instructor Portal dashboard, Calendar UI, and Messaging UI
- `DEVELOPMENT_PLAN.md` — Expanded Module 5 (Instructors) with login, calendar, messaging, debt tracking; expanded Module 16 (Dashboard) with admin and instructor dashboard specs
- `CLAUDE.md` — Added Section 13 (Instructor Portal & Permissions)

---

## [0.3.0] - 2026-03-09

### PDF Templates & UI Design Guidelines

#### Added
- `docs/PDF_TEMPLATES.md` — Comprehensive PDF layout specifications for all 7 document types (Fatura, Fleteparaqitja, Libreza, Kontrata, Testi, Vertetimi, Candidate List) with exact layout, CSS, template variables, and implementation checklist
- `docs/UI_DESIGN_GUIDELINES.md` — Full frontend modernization guidelines with color palette, typography, layout structure, data table design, form wizard patterns, dashboard design, responsive breakpoints, accessibility, and Albanian-specific UI patterns

#### Changed
- `CLAUDE.md` — Added Section 11 (PDF Generation — 100% Fidelity Required) and Section 12 (Frontend UI — Modern Redesign), updated project structure to include new docs
- Original CRM reference screenshots captured for: Fatura, Fleteparaqitja (2 pages), Libreza (2 pages), Kontrata, Testi (4 pages), Candidates list, Payments page

---

## [0.2.0] - 2026-03-09

### Architecture Restructure — poolgo-ops Pattern

#### Changed
- **Removed Docker**: No more Docker Compose, Dockerfiles, or containerization. Dev runs via Python venv + `python wsgi.py` on port 5002
- **Replaced Flask-JWT-Extended with PyJWT**: Custom JWT encode/decode in `app/utils/jwt.py`
- **Replaced `routes/` with `api/`**: Single `api_bp` Blueprint in `app/api/__init__.py` (poolgo-ops pattern)
- **Replaced `extensions.py` with `utils/db.py`**: SQLAlchemy + Flask-Migrate initialization
- **Added middleware chain** (poolgo-ops pattern):
  - `request_id.py` — X-Request-Id header
  - `auth_context.py` — Extract JWT → `g.current_user`, `g.tenant_id`
  - `api_auth_guard.py` — Enforce auth on `/api/v1/*` with PUBLIC_PATHS exemption
  - `response_envelope.py` — Wrap all responses in `{success, data}` envelope
  - `error_handler.py` — Custom exceptions (ValidationError, Unauthorized, Forbidden, NotFound)
- **Added Pydantic validation**: `BaseSchema` in `utils/validation.py`, schemas in `app/schemas/`
- **Backend port changed**: 5000 → 5002

#### Added
- `backend/app/api/health.py` — Health check endpoint
- `backend/app/api/auth.py` — Login, refresh, logout, me endpoints
- `backend/app/schemas/auth.py` — LoginSchema, RefreshSchema
- `backend/app/services/auth_service.py` — Auth business logic
- `backend/app/models/tenant_model.py` — Tenant SQLAlchemy model
- `backend/app/models/user_model.py` — User SQLAlchemy model with bcrypt
- `backend/app/utils/jwt.py` — PyJWT encode/decode with duration parsing
- `backend/app/utils/serialization.py` — JSON serializer for UUID/datetime
- `backend/app/utils/pagination.py` — SQLAlchemy pagination helper
- `backend/tests/conftest.py` — pytest fixtures (app, client, db)
- `backend/.env` — Local dev environment variables
- `backend/wsgi.py` — Entry point (port 5002)

#### Removed
- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/app/extensions.py`
- `backend/app/routes/` directory

#### Documentation Updated
- `CLAUDE.md` — Updated tech stack, project structure, code conventions, how to run (venv + port 5002)
- `docs/OVERVIEW.md` — Updated tech stack, deployment, added poolgo-ops architecture section
- `DEVELOPMENT_PLAN.md` — Removed Docker references, updated Module 1 structure, port 5002

---

## [0.1.0] - 2026-03-09

### Project Initialization

#### Added

**Documentation**
- Created `OVERVIEW.md` - Complete architecture overview document
  - Project description and technology stack
  - ASCII architecture diagram
  - Multi-tenancy approach explanation
  - Authentication flow diagrams
  - PDF generation strategy with WeasyPrint and Jinja2
  - Testing strategy and testing pyramid
  - 7 key design decisions with rationale and trade-offs
  - Compliance and deployment architecture sections

- Created `API_REFERENCE.md` - Full API endpoint reference
  - 15 API modules documented
  - 80+ endpoints with HTTP methods, paths, request bodies, and responses
  - Auth module: login, refresh, logout, me, impersonate, exit-impersonate
  - Locations module: countries, municipalities, places
  - School module: profile and licenses CRUD
  - Categories module: full CRUD
  - Instructors module: CRUD and candidates list
  - Vehicles module: CRUD
  - Candidates module: CRUD, search, archive, supplementary, export
  - Theory Hours module: sessions and bulk upload
  - Practical Hours module: CRUD with filters
  - Payments module: CRUD and by-candidate
  - Verifications module: CRUD
  - Expenses module: CRUD and types
  - Users module: CRUD, password reset, toggle active
  - Print/PDF module: 7 document types (Fatura, Fleteparaqitja, Libreza, Kontrata, Vertetimi, Testi, candidate lists)
  - Super Admin module: tenants, statistics, audit logs
  - Common response patterns and error handling
  - Rate limiting, file upload, and date/time format specifications

- Created `MODULES_STATUS.md` - Module completion tracker
  - Status table with 16 modules and completion percentages
  - Status legend with 7 status values
  - Module dependencies diagram
  - Recommended implementation order (5 phases)
  - Detailed completion criteria for each module
  - Performance targets (API response, PDF generation, query times)
  - Current phase indicator: Phase 0 - Project Initialization

- Created `CHANGELOG.md` - This file
  - Version history tracking
  - Change categorization (Added, Changed, Deprecated, Removed, Fixed, Security)
  - Initial entry for project initialization on 2026-03-09

**Project Structure**
- Initialized project directory structure:
  - `/docs` directory for all documentation
  - `/scripts` directory for database and utility scripts
  - `/app` directory for main application code (backend)
  - `/frontend` directory for Next.js frontend code
  - `/tests` directory for test suites

**Database Schema**
- Created comprehensive database schema documentation
- Defined 20 tables with relationships:
  - Reference tables: countries, municipalities, places
  - Tenant tables: tenants, users, sessions
  - School management: categories, licenses, instructors, vehicles
  - Candidate lifecycle: candidates, theory_hour_sessions, practical_hour_sessions, supplementary_registrations, verifications, candidate_tests
  - Finance: payments, expense_types, expenses
  - Audit: audit_logs
- Defined indexes for performance optimization
- Specified constraints and validations

**Configuration Files**
- Created core project configuration infrastructure
- Set up development and production environment templates
- Created requirements files for Python dependencies

### System Architecture

- **Multi-Tenancy**: Shared database model with row-level isolation via tenant_id
- **Authentication**: JWT-based with refresh token rotation and super-admin impersonation support
- **Authorization**: Role-based access control with 4 roles (super_admin, administrator, instructor, lecturer)
- **PDF Generation**: WeasyPrint + Jinja2 templates for 7 document types
- **Testing**: pytest for unit/integration, Playwright for E2E
- **Database**: PostgreSQL with UUID primary keys and comprehensive constraints

### Status

- All 16 modules at 0% completion
- Project structure initialized
- Documentation complete
- Database schema documented
- Ready to begin Phase 1 implementation

---

## Version History Notes

### Versioning Strategy

- **Major version** (1.0.0): Major feature releases, breaking API changes
- **Minor version** (0.1.0): New modules, new features, backward compatible
- **Patch version** (0.1.1): Bug fixes, documentation updates

### Release Schedule

- **Alpha** (0.x.x): Core functionality in development
- **Beta** (1.0.0-beta): Feature complete, testing phase
- **Release** (1.0.0): Production ready

---

## How to Update This Changelog

When making changes to the project:

1. Add entries under `[Unreleased]` section
2. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Link related issues/PRs using format: `[GH-123](https://github.com/org/repo/pull/123)`
4. When releasing, move entries from `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`
5. Add new `[Unreleased]` section at top

### Example Entry

```markdown
### Added
- New user dashboard with real-time statistics [GH-456](link)
- Export candidates to PDF with custom templates [GH-457](link)

### Fixed
- Fixed payment date validation bug [GH-458](link)

### Changed
- Updated authentication middleware for better performance [GH-459](link)
```

---

## Archived Versions

None yet - project just initialized.

