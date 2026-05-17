# AutoShkolla Pro - Agent Instructions

## Project Name

**autoshkolla-pro** — Multi-tenant Driving School Management System for Kosovo

## Tech Stack

- **Backend**: Python 3.11+, Flask, SQLAlchemy, PyJWT, Flask-Migrate, WeasyPrint, Pydantic
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, React Query (TanStack Query), Zustand
- **Database**: PostgreSQL 15+ (local dev, Supabase for production later)
- **Testing**: pytest (unit + integration), Playwright (E2E), pytest-cov for coverage
- **PDF Engine**: WeasyPrint with Jinja2 HTML templates
- **Dev Environment**: Python venv (no Docker)

## Architecture

- REST API pattern: Flask backend serves JSON API, Next.js frontend consumes it
- Multi-tenancy: Shared database with `tenant_id` column on all tenant-scoped tables
- Authentication: JWT tokens (access + refresh) via PyJWT (custom implementation, NOT Flask-JWT-Extended)
- Super-admin: Separate role that can manage all tenants and impersonate users
- Architecture follows the **poolgo-ops** pattern: simple `create_app()` factory, `init_`* middleware, single API Blueprint, Pydantic validation, response envelope

## Language

- The entire UI is in **Albanian** (Kosovo dialect). All labels, buttons, form fields, and messages must be in Albanian.
- Code (variables, functions, comments) should be in **English**.
- Database column names are in **English**.

## Project Structure

```
autoshkolla-pro/
├── CLAUDE.md                    # THIS FILE - read first!
├── DEVELOPMENT_PLAN.md          # Full feature specification
├── .env.example                 # Environment variable template
├── docs/                        # Agent documentation (READ & UPDATE!)
│   ├── OVERVIEW.md              # Architecture and conventions
│   ├── DATABASE_SCHEMA.md       # Full schema documentation
│   ├── API_REFERENCE.md         # API endpoint reference
│   ├── MODULES_STATUS.md        # Module completion status tracker
│   ├── CHANGELOG.md             # Log of all changes
│   ├── PDF_TEMPLATES.md         # PDF layout specs (100% fidelity required)
│   ├── UI_DESIGN_GUIDELINES.md  # Frontend modernization guidelines
│   └── SMS_NOTIFICATIONS.md    # Bulk SMS feature spec (deferred)
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory (create_app with init_* middleware)
│   │   ├── config.py            # Single Config class (env vars)
│   │   ├── api/                 # Single Blueprint for all API routes
│   │   │   ├── __init__.py      # api_bp Blueprint + route imports
│   │   │   ├── health.py        # GET /health
│   │   │   └── auth.py          # Auth endpoints (login, refresh, logout, me)
│   │   ├── schemas/             # Pydantic validation schemas
│   │   ├── services/            # Business logic layer
│   │   ├── models/              # SQLAlchemy models (one file per model, *_model.py)
│   │   ├── middleware/          # Request processing middleware
│   │   │   ├── auth_context.py  # Extract JWT → set g.current_user, g.tenant_id
│   │   │   ├── api_auth_guard.py # Enforce auth on /api/v1/* (PUBLIC_PATHS exempt)
│   │   │   ├── error_handler.py # Custom exceptions + JSON error responses
│   │   │   ├── response_envelope.py # Wrap responses in {success, data} envelope
│   │   │   └── request_id.py    # X-Request-Id header
│   │   ├── utils/               # Helpers
│   │   │   ├── db.py            # SQLAlchemy + Flask-Migrate init
│   │   │   ├── jwt.py           # PyJWT encode/decode helpers
│   │   │   ├── validation.py    # Pydantic BaseSchema + parse_body/parse_query
│   │   │   ├── serialization.py # JSON serializer (UUID, datetime)
│   │   │   └── pagination.py    # SQLAlchemy pagination helper
│   │   ├── pdf/                 # PDF generation
│   │   │   ├── templates/       # Jinja2 HTML templates for each PDF type
│   │   │   ├── styles/          # CSS for PDF styling
│   │   │   └── assets/          # Images (coat of arms, logos)
│   │   └── seeds/               # Database seed scripts
│   ├── migrations/              # Alembic migration files
│   ├── tests/
│   │   ├── conftest.py          # Shared pytest fixtures
│   │   ├── unit/                # Unit tests (per model, per service)
│   │   ├── integration/         # API route integration tests
│   │   └── e2e/                 # Playwright end-to-end tests
│   ├── requirements.txt
│   ├── .env                     # Local dev environment vars
│   └── wsgi.py                  # Entry point: python wsgi.py (port 5002)
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   ├── components/              # React components by domain
│   ├── lib/                     # API client, auth, types, utils
│   ├── hooks/                   # Custom React hooks
│   ├── public/                  # Static assets
│   ├── styles/                  # Global CSS
│   ├── package.json
│   └── next.config.js
└── scripts/                     # Utility scripts (seed, migrate, etc.)
```

## Critical Rules for ALL Agents

### 1. Multi-tenancy is MANDATORY

- Every tenant-scoped model MUST have a `tenant_id` column
- Every query MUST filter by `g.tenant_id` (set by middleware)
- NEVER expose data from one tenant to another
- Use the `TenantMixin` base class for all tenant-scoped models
- Location reference data (countries, municipalities, places) is shared (no tenant_id)

### 2. Testing is MANDATORY

- **Every change MUST include tests**
- Unit tests for every model method and service function
- Integration tests for every API endpoint
- Playwright E2E tests for every frontend user flow
- Run `pytest` before committing — all tests must pass
- Target: 80%+ code coverage

### 3. Documentation is MANDATORY

After EVERY change, agents MUST:

1. Update `CLAUDE.md` if conventions change
2. Create/update a file in `/docs/` describing what was done
3. Update `docs/MODULES_STATUS.md` with completion percentage
4. Update `docs/CHANGELOG.md` with a dated entry
5. Update `docs/API_REFERENCE.md` if API endpoints changed
6. Update `docs/DATABASE_SCHEMA.md` if schema changed

### 4. Code Conventions

#### Python (Backend) — poolgo-ops pattern

- Use type hints everywhere
- **Pydantic** for request/response validation (BaseSchema in `utils/validation.py`)
- One model per file in `models/` named `{name}_model.py`
- **Single API Blueprint** (`api_bp`) in `api/__init__.py` — all routes registered here
- Business logic goes in `services/`, NOT in routes
- Use Flask's `g` object for tenant context (`g.tenant_id`, `g.current_user`)
- All dates stored as UTC in database, formatted as `dd.MM.yyyy` for Albanian UI
- **Response envelope**: All JSON responses wrapped in `{"success": true, "data": ...}`
- **Error handling**: Custom exceptions (ValidationError, Unauthorized, Forbidden, NotFound) in `middleware/error_handler.py`
- **Auth**: PyJWT for token encode/decode (NOT Flask-JWT-Extended)
- Auth context middleware extracts JWT from `Authorization` header or cookie → sets `g.current_user`
- API auth guard enforces auth on all `/api/v1/`* except PUBLIC_PATHS

#### TypeScript (Frontend)

- Strict TypeScript — no `any` types
- Use React Server Components where possible
- Client components marked with `'use client'`
- API calls via centralized `lib/api.ts` (axios with JWT interceptor)
- State management: Zustand for global state, React Query for server state
- All form validation using Zod schemas
- Components organized by domain (candidates/, payments/, etc.)

#### Database

- Use snake_case for all column names
- Use UUID for primary keys (ready for Supabase)
- All tenant-scoped tables have `tenant_id` as a non-nullable FK
- Timestamps: `created_at`, `updated_at` on all tables
- Soft delete where appropriate: `deleted_at` timestamp
- Foreign keys with proper ON DELETE behavior
- Indexes on: `tenant_id`, frequently filtered columns, foreign keys

#### Naming Conventions

- API routes: `/api/v1/{resource}` (e.g., `/api/v1/candidates`, `/api/v1/payments`)
- Frontend routes: `/(dashboard)/{section}/page.tsx`
- Model files: `{name}_model.py` (e.g., `tenant_model.py`, `candidate_model.py`)
- Schema files: `{module}.py` in `schemas/` (e.g., `schemas/auth.py`)
- Test files: `test_{module}.py` (backend), `{component}.test.tsx` (frontend)
- Migration files: auto-generated by Alembic

### 5. Git Workflow

- Feature branches: `feature/module-{number}-{name}` (e.g., `feature/module-7-candidates`)
- Commit messages: `[Module X] description` (e.g., `[Module 7] Add candidate CRUD API endpoints`)
- All commits must pass tests

### 6. Albanian UI Reference

Key translations used throughout the system:

- Kandidatet = Candidates
- Instruktor = Instructor
- Ligjerues = Lecturer
- Automjetet = Vehicles
- Shpenzimet = Expenses
- Pagesat = Payments
- Kategoria = Category
- Ore Teorike = Theory Hours
- Ore Praktike = Practical Hours
- Ore Plotesuese = Supplementary Hours
- Vërtetimi = Verification Certificate
- Fatura = Invoice
- Fletëparaqitja = Submission Form
- Libreza = Booklet
- Kontrata = Contract
- Arkiva = Archive
- Evidenca Oreve = Hours Evidence
- Kerko = Search
- Registro = Register
- Ruaj = Save
- Mbyll = Close
- Anulo = Cancel
- Fshi = Delete
- Edito = Edit
- Paguaj = Pay
- Paneli = Dashboard
- Kalendari = Calendar
- Mesazhet = Messages
- Borxhi = Debt
- Profili Im = My Profile
- Kandidatët e Mi = My Candidates
- Mësimet Sot = Today's Lessons
- Pagesat e Instruktorëve = Instructor Payments
- Planifiko = Schedule
- Alarmet = Alerts

### 7. Module Dependencies

Before working on a module, verify its dependencies are complete:

```
Module 1 (Auth)          → No dependencies
Module 2 (Locations)     → Module 1
Module 3 (School)        → Module 1, 2
Module 4 (Categories)    → Module 1
Module 5 (Instructors)   → Module 1
Module 6 (Vehicles)      → Module 1, 5
Module 7 (Candidates)    → Module 1, 2, 4, 5, 6
Module 8 (Theory Hours)  → Module 7
Module 9 (Practical Hrs) → Module 7, 5
Module 10 (Payments)     → Module 7
Module 11 (Verification) → Module 7, 8, 9
Module 12 (Expenses)     → Module 1, 6
Module 13 (Users)        → Module 1
Module 14 (PDF Gen)      → Module 7, 8, 9, 11
Module 15 (Super Admin)  → Module 1
Module 16 (Dashboard/UI) → Module 1
```

### 8. How to Run

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask seed-locations  # Seed Kosovo geographic data
python wsgi.py        # Runs on port 5002

# Frontend
cd frontend
npm install
npm run dev           # Runs on port 3000

# Tests
cd backend && pytest -v --cov=app
cd frontend && npm run test
cd backend && playwright test  # E2E
```

```bash
# Import legacy candidates (one-time migration)
cd backend && source venv/bin/activate
python ../scripts/import_candidates.py --tenant-slug autoshkolla-demo       # live import
python ../scripts/import_candidates.py --tenant-slug autoshkolla-demo --dry-run  # preview only
```

**Important**: No Docker. Use Python venv directly. Backend runs on **port 5002**.

### 9. Environment Variables

See `.env.example` for all required variables. Key ones:

- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://autoshkolla:dev_password@localhost:5432/autoshkolla_pro`)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET` - Secret for JWT signing
- `FLASK_ENV` - development/production
- `CORS_ORIGIN` - Frontend URL (default: `http://localhost:3000`)

### 10. Reference Architecture

This project follows the **poolgo-ops** Flask pattern. Key architectural decisions:

- `create_app()` factory with `init_`* middleware functions (not Flask extensions)
- Single `api_bp` Blueprint registered at `/api/v1`
- Middleware chain: request_id → auth_context → api_auth_guard → response_envelope → error_handlers
- Pydantic `BaseSchema` with `extra='forbid'` for strict input validation
- `parse_body()` / `parse_query()` helpers for request parsing
- Response envelope: `{"success": true, "data": ...}` for all success responses
- Custom exception classes map to HTTP status codes automatically

### 11. PDF Generation — 100% Fidelity Required

- **PDF printouts MUST be 100% identical to the original system's output**
- See `docs/PDF_TEMPLATES.md` for exact layout specifications of all 7 document types
- Engine: WeasyPrint + Jinja2 HTML templates
- Templates: `backend/app/pdf/templates/{document_type}.html`
- Shared CSS: `backend/app/pdf/styles/pdf_base.css`
- Assets: `backend/app/pdf/assets/` (Kosovo coat of arms, school logos)
- 7 document types: Fatura (Invoice), Fleteparaqitja (Registration Form), Libreza (Logbook), Kontrata (Contract), Testi (Test Result), Vertetimi (Certificate), Candidate List
- Date format throughout: `dd.MM.yyyy`, Currency: Euro (€)
- Albanian characters (ë, ç) must render correctly — use DejaVu Sans or similar
- Government forms (Fleteparaqitja, Vertetimi) require Kosovo coat of arms and trilingual headers
- Each PDF template should be visually verified against the original before marking complete

### 12. Frontend UI — Modern Redesign

- **The UI must be fully modernized** — the original system is old-school Bootstrap 3
- See `docs/UI_DESIGN_GUIDELINES.md` for comprehensive design specifications
- Keep 100% of the business logic and workflows — only modernize the appearance
- Tech: Next.js 14 + Tailwind CSS + shadcn/ui + Lucide icons
- Key improvements over original:
  - Collapsible sidebar with grouped navigation (6 groups instead of 16+ flat items)
  - Smart data tables with column visibility, advanced filters, status badges
  - Multi-step wizard for candidate registration (instead of 30+ fields on one page)
  - Tab-based candidate detail page (Personal, Theory Hours, Practical, Payments, Documents, History)
  - Proper dashboard with metrics, schedule, activity feed
  - Mobile-responsive for tablet use by instructors
- Color palette: Modern blue primary (#2563EB), clean grays, proper semantic colors
- Font: Inter with Albanian character support
- All UI text in Albanian (Kosovo dialect) — see Albanian UI Reference in section 6

### 13. Instructor Portal & Permissions

- **Instructors have login capability**: When creating an instructor with email + password, a `users` record is auto-created with `role='instructor'` and linked via `instructor.user_id`
- **Instructor permissions are READ-ONLY for candidates**: Instructors can only view candidates assigned to them. They CANNOT create, edit, or delete candidates
- **Instructor Portal** (`/instructor/`*): Separate layout with its own sidebar and dashboard
  - Dashboard: Active candidates count, today's lessons, debt balance, unread messages
  - My Candidates: Read-only list of assigned candidates with progress info
  - Calendar: Interactive calendar for practical lesson scheduling (day/week/month views)
  - Debt/Payments: 65€ per candidate charge tracking. Shows total owed, total paid, balance, per-candidate breakdown
  - Messages: Threaded communication with school admins
- **Instructor Debt Model**: Each assigned candidate incurs a 65€ charge (configurable via `instructor.cost_per_candidate`). An `instructor_payments` record is auto-created when a candidate is assigned. Admins record payments to reduce the balance
- **Calendar / Scheduling**: `scheduled_lessons` table tracks practical lesson appointments. When a lesson is marked "completed", it auto-creates a `practical_hour_sessions` record. Statuses: scheduled, completed, cancelled, no_show
- **Messaging**: `conversations` + `messages` tables for threaded communication between instructors and admins within the same tenant
- **Admin Dashboard**: Comprehensive dashboard as landing page — metrics cards, revenue charts, category breakdown, today's schedule, activity feed, alerts (expiring docs, overdue payments, instructor debt)
- **Role-based routing**: After login, redirect to `/superadmin` (super_admin), `/dashboard` (admins/lecturers), or `/instructor` (instructors) based on `user.role`
- **Super-Admin Panel** (`/superadmin/`*): Dedicated layout with red color scheme, own sidebar
  - Tenants: Full CRUD for driving schools, expand to see/add/edit users, impersonate any user
  - Statistics: Platform-wide stats (tenants, users, candidates, active/archived)
  - Super-admins are redirected away from `/dashboard` — they must impersonate to view tenant data
- **Settings Page** (`/dashboard/cilesimet`): Account info display and password change for admins

