# AutoShkolla Pro - Driving School Management System
## Development Plan: Flask + Next.js Rebuild

> **Project Name**: `autoshkolla-pro`
> **Original System**: autoshkolla.solution-ks.com (ASP.NET MVC)
> **Target Stack**: Flask (backend) + Next.js (frontend) + PostgreSQL

---

## 1. Project Overview

Rebuild the existing Kosovo driving school CRM (autoshkolla.solution-ks.com) as a modern, multi-tenant SaaS application. The current system is built on ASP.NET MVC with server-rendered views, jQuery, and Bootstrap. The rebuild targets **Flask (Python backend API)** + **Next.js (React frontend)** with multi-tenancy, super-admin impersonation, and modular architecture.

### Key Requirements
- Full Albanian language UI (same as current system)
- Multi-tenant architecture: each Autoshkollë (driving school) is a tenant with isolated data
- Every user belongs to a tenant and can ONLY see/modify data within their tenant
- Super-admin panel to manage all tenants + impersonate any user in any tenant
- PDF generation for 7 document types (matching current layouts exactly)
- Role-based access control (SuperAdmin, Administrator, Instructor, Lecturer)
- PostgreSQL database (local dev, Supabase for production)
- Modular feature separation for parallel agent development
- **Mandatory unit tests** for every change (pytest + Playwright E2E)
- **Mandatory documentation updates** after every change (CLAUDE.md + /docs/)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Next.js Frontend                   │
│  (Pages, Components, State Management, PDF Preview)   │
│                    Port: 3000                          │
└──────────────────────┬──────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────┴──────────────────────────────┐
│                    Flask Backend                      │
│  (API Routes, Auth, Business Logic, PDF Generation)   │
│                    Port: 5002                          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────┐
│              PostgreSQL Database                      │
│  (Multi-tenant with tenant_id on all tables)          │
│                    Port: 5432                          │
└─────────────────────────────────────────────────────┘
```

### Tech Stack
- **Backend**: Flask, SQLAlchemy, PyJWT, Flask-Migrate, WeasyPrint (PDF), Celery (background tasks)
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, React Query, Zustand
- **Database**: PostgreSQL with multi-tenant schema (shared database, tenant_id column)
- **Auth**: JWT tokens with refresh, role-based permissions
- **PDF**: WeasyPrint with Jinja2 HTML templates (matching current PDF layouts)
- **Dev Environment**: Python venv (no Docker)

---

## 3. Database Schema

### Core Tables

```sql
-- TENANT & AUTH
tenants (id, name, nui, tvsh, email, phone, address, representative, bank_name, bank_account, logo_url, license_number, city, is_active, created_at, updated_at)
users (id, tenant_id, username, password_hash, full_name, personal_number, email, role, is_active, activation_count, created_at, end_date)
sessions (id, user_id, token, refresh_token, expires_at, impersonated_by)

-- LOCATION REFERENCE DATA (shared across tenants)
countries (id, name)  -- Kosovë, Jasht Kosove
municipalities (id, country_id, name)  -- 40 municipalities: Prishtinë, Ferizaj, etc.
places (id, municipality_id, name)  -- Villages/cities within municipalities

-- DRIVING SCHOOL CONFIG
categories (id, tenant_id, code, description, verification_text, verification_code, theory_hours, practical_hours, price, contract_price, is_licensed, is_active)
-- Categories: B, BD, C, CE, D

licenses (id, tenant_id, category_id, license_code, issue_date, expiry_date)

-- STAFF
instructors (id, tenant_id, user_id, code, first_name, last_name, personal_number, email, phone, position, hours_realized, is_active, license_info, cost_per_candidate)
-- position: 'instructor' | 'lecturer' | 'both'
-- user_id: FK → users.id (for instructor login, auto-created when email+password provided)

-- VEHICLES
vehicles (id, tenant_id, make, model, chassis_number, plate_number, registration_date, registration_expiry, technical_control_date, instructor_id, is_active)

-- CANDIDATES (core entity)
candidates (id, tenant_id, code, first_name, parent_name, last_name, personal_number, phone, email, birth_country_id, birth_municipality_id, birth_place_id, birth_municipality_foreign, birth_place_foreign, date_of_birth, gender, residence_municipality_id, residence_place_id, category_id, is_automatic, price, amount_paid, practical_hours, theory_hours, registration_date, protocol_number, medical_certificate, medical_certificate_number, medical_certificate_date, verification_flag, red_cross_certificate, id_card_copy, lecturer_id, instructor_id, vehicle_id, has_extra_hours, is_archived, comments, created_at, updated_at)

-- THEORY HOURS TRACKING
theory_hour_sessions (id, candidate_id, tenant_id, session_number, chapter_topics, date_realized, time_from, time_to, hours_count, is_realized)
-- 8 sessions per candidate for category B, each covering specific chapter groupings

-- PRACTICAL HOURS TRACKING
practical_hour_sessions (id, candidate_id, tenant_id, instructor_id, date_realized, time_realized, hours_count, price_per_hour, remarks, is_paid, created_at)

-- SUPPLEMENTARY HOURS (ore plotesuese)
supplementary_registrations (id, candidate_id, tenant_id, category_id, is_automatic, price, practical_hours, theory_hours, registration_date, created_at)

-- VERIFICATION (vertetim)
verifications (id, candidate_id, tenant_id, category_id, verification_date, theory_start_date, theory_end_date, practical_start_date, practical_end_date, sequence_number, lecturer_id, instructor_id, red_cross_cert, id_card_copy, created_at)

-- PAYMENTS
payments (id, candidate_id, tenant_id, amount, payment_method, payment_date, received_by, is_supplementary, remarks, created_at)

-- EXPENSES
expense_types (id, tenant_id, name, is_active)
expenses (id, tenant_id, vehicle_id, expense_type_id, date, amount, description, created_at)

-- TESTS (basic structure, not the paid module)
candidate_tests (id, candidate_id, tenant_id, test_number, score, passing_score, date_taken, is_passed, created_at)

-- INSTRUCTOR PAYMENTS (debt tracking — 65€ per candidate)
instructor_payments (id, tenant_id, instructor_id, candidate_id, amount, amount_paid, payment_date, payment_method, status, remarks, created_at)
-- status: 'unpaid' | 'partial' | 'paid'
-- auto-created when candidate assigned to instructor

-- MESSAGING (instructor ↔ admin communication)
conversations (id, tenant_id, subject, participant_ids, last_message_at, created_by, created_at)
messages (id, tenant_id, conversation_id, sender_id, recipient_id, content, is_read, read_at, created_at)

-- CALENDAR / SCHEDULING
scheduled_lessons (id, tenant_id, instructor_id, candidate_id, vehicle_id, scheduled_date, start_time, end_time, status, notes, cancelled_reason, practical_session_id, created_at)
-- status: 'scheduled' | 'completed' | 'cancelled' | 'no_show'
-- When completed → auto-creates practical_hour_sessions record
```

---

## 4. Feature Modules (Separated for Parallel Development)

Each module below is self-contained and can be developed by a separate agent. Modules are listed with their dependencies.

---

### MODULE 1: Authentication & Multi-tenancy Core
**Priority: P0 (must be first)**
**Dependencies: None**
**Estimated effort: 2-3 days**

#### Backend (Flask)
```
backend/
├── app/__init__.py              # Flask app factory
├── app/config.py                # Environment config
├── app/models/
│   ├── tenant.py                # Tenant model
│   ├── user.py                  # User model with password hashing
│   └── session.py               # Session/token model
├── app/api/
│   └── auth.py                  # POST /auth/login, /auth/refresh, /auth/logout
├── app/schemas/
│   └── auth_schemas.py          # Request/response validation schemas
├── app/middleware/
│   ├── api_auth_guard.py        # @require_auth, @require_role, @require_tenant
│   ├── tenant_context.py        # Extract tenant from JWT, set g.tenant_id
│   ├── response_envelope.py     # Standard response wrapping
│   ├── request_id.py            # Request ID tracking
│   └── audit_log.py             # Log all mutations
├── app/utils/
│   ├── db.py                    # SQLAlchemy initialization
│   ├── jwt.py                   # PyJWT utilities
│   ├── permissions.py           # Role-based permission checks
│   └── impersonation.py         # Super-admin impersonation logic
└── migrations/                  # Alembic migrations
```

#### Frontend (Next.js)
```
frontend/
├── app/
│   ├── login/page.tsx           # Login page
│   └── layout.tsx               # Root layout with auth provider
├── lib/
│   ├── api.ts                   # Axios instance with JWT interceptor
│   ├── auth-context.tsx         # Auth context provider
│   └── types/auth.ts            # Auth types
├── components/
│   └── auth/
│       ├── LoginForm.tsx
│       └── ProtectedRoute.tsx
└── middleware.ts                 # Next.js middleware for auth redirect
```

#### Key Features
- JWT login with refresh tokens
- Multi-tenant context injection via middleware (every DB query filtered by tenant_id)
- Role-based route protection: SuperAdmin, Administrator, Instructor, Lecturer
- Super-admin impersonation: POST /auth/impersonate/{tenant_id}/{user_id}
  - Stores original admin session, creates impersonated session
  - Yellow banner in UI showing "Impersonating: [School Name] as [User]"
  - "Exit impersonation" button to return to super-admin
- Session management: 60-minute timeout (matching current "Aktive edhe: 60 min")
- Password hashing with bcrypt

#### API Endpoints
```
POST   /api/auth/login            # { username, password } → { access_token, refresh_token, user, tenant }
POST   /api/auth/refresh           # { refresh_token } → { access_token }
POST   /api/auth/logout            # Invalidate session
POST   /api/auth/impersonate       # SuperAdmin only: { tenant_id, user_id }
POST   /api/auth/exit-impersonate  # Return to super-admin session
GET    /api/auth/me                # Current user + tenant info
```

---

### MODULE 2: Location Reference Data & Shared Config
**Priority: P0**
**Dependencies: Module 1**
**Estimated effort: 1 day**

#### Backend
```
backend/app/
├── models/
│   ├── country.py
│   ├── municipality.py
│   └── place.py
├── api/
│   └── locations.py             # GET endpoints for cascading dropdowns
└── seeds/
    └── locations.py             # Seed script for Kosovo municipalities & places
```

#### Key Features
- Countries: Kosovë (id=1), Jasht Kosove (id=2)
- 40 municipalities with IDs (Ferizaj=3, Prishtinë=1, etc.)
- Places/villages within each municipality (dynamically loaded)
- Cascading dropdown API: GET /api/locations/municipalities?country_id=1 → GET /api/locations/places?municipality_id=3
- Seed script to populate all Kosovo geographic data

#### API Endpoints
```
GET    /api/locations/countries
GET    /api/locations/municipalities?country_id={id}
GET    /api/locations/places?municipality_id={id}
```

---

### MODULE 3: Driving School Profile & Licenses
**Priority: P1**
**Dependencies: Module 1, Module 2**
**Estimated effort: 1-2 days**

#### Backend
```
backend/app/
├── models/
│   ├── driving_school.py        # Extends tenant with school-specific fields
│   └── license.py
├── api/
│   └── school.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── school/
│       ├── page.tsx             # School details view
│       ├── edit/page.tsx        # Edit school info
│       └── licenses/page.tsx    # License management
├── components/
│   └── school/
│       ├── SchoolInfoCard.tsx
│       └── LicenseTable.tsx
```

#### Key Features
- View/edit school profile: name, NUI, TVSH, email, phone, address, representative
- License management per category (B, CE, C, D): license code, issue date, expiry date
- School-specific branding for PDF documents (logo, bank details)

#### API Endpoints
```
GET    /api/school                 # Current tenant's school details
PUT    /api/school                 # Update school details
GET    /api/school/licenses        # List licenses
POST   /api/school/licenses        # Add license
PUT    /api/school/licenses/{id}   # Update license
DELETE /api/school/licenses/{id}   # Delete license
```

---

### MODULE 4: Category Administration
**Priority: P1**
**Dependencies: Module 1**
**Estimated effort: 1 day**

#### Backend
```
backend/app/
├── models/
│   └── category.py
├── api/
│   └── categories.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── admin/
│       └── categories/
│           └── page.tsx         # Category CRUD table
├── components/
│   └── admin/
│       └── CategoryForm.tsx     # Modal form for add/edit
```

#### Key Features
- CRUD for driving categories (B, BD, C, CE, D)
- Per-category config: description, theory hours, practical hours, price, contract price
- Verification text and code per category
- License flag and active status toggles

#### API Endpoints
```
GET    /api/categories
POST   /api/categories
PUT    /api/categories/{id}
DELETE /api/categories/{id}
```

---

### MODULE 5: Instructor & Lecturer Management
**Priority: P1**
**Dependencies: Module 1**
**Estimated effort: 3-4 days**

#### Backend
```
backend/app/
├── models/
│   ├── instructor_model.py
│   ├── instructor_payment_model.py
│   ├── scheduled_lesson_model.py
│   ├── conversation_model.py
│   └── message_model.py
├── api/
│   ├── instructors.py           # Admin CRUD + instructor self-service
│   ├── instructor_payments.py   # Debt tracking endpoints
│   ├── scheduled_lessons.py     # Calendar/scheduling endpoints
│   └── messages.py              # Instructor ↔ Admin messaging
├── services/
│   ├── instructor_service.py    # Instructor business logic
│   ├── instructor_payment_service.py  # Debt calculation
│   ├── scheduling_service.py    # Calendar/conflict resolution
│   └── message_service.py       # Messaging logic
├── schemas/
│   ├── instructor.py
│   ├── instructor_payment.py
│   ├── scheduled_lesson.py
│   └── message.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── instructors/
│       ├── page.tsx                 # Admin: list with 19+ instructors
│       └── [id]/page.tsx            # Admin: instructor detail + debt view
├── (instructor)/                    # INSTRUCTOR PORTAL (separate layout)
│   ├── layout.tsx                   # Instructor-specific layout
│   ├── page.tsx                     # Instructor dashboard (overview)
│   ├── candidates/page.tsx          # My candidates (read-only)
│   ├── calendar/page.tsx            # Practical lesson calendar
│   ├── payments/page.tsx            # My debt & payment history
│   └── messages/page.tsx            # Communication with admins
├── components/
│   └── instructors/
│       ├── InstructorTable.tsx      # Admin: sortable table
│       ├── InstructorForm.tsx       # Admin: add/edit modal (email+password)
│       ├── InstructorDebtTable.tsx  # Debt tracking table
│       ├── LessonCalendar.tsx       # Interactive calendar component
│       ├── LessonScheduleForm.tsx   # Schedule a new lesson
│       └── MessageThread.tsx        # Messaging component
```

#### Key Features

**Admin-side (Instructor Management)**:
- List instructors with: position (Instruktor/Ligjerues), personal number, phone, email, hours realized, assigned vehicle, active clients count, license info, total debt
- CRUD operations — when creating, include **email** and **password** fields
- Creating an instructor with email+password auto-creates a `users` record with `role='instructor'` and links via `instructor.user_id`
- Position types: Instruktor (driving instructor), Ligjerues (lecturer), or both
- Assignment to vehicles
- Hours tracking and reporting
- View instructor debt summary (total owed, total paid, balance)
- Record instructor payments

**Instructor Portal (Self-Service)**:
- **Login**: Instructors log in with their email + password (same JWT auth as admins, but `role='instructor'`)
- **Dashboard**: Overview showing — active candidates count, upcoming lessons today/this week, total debt, recent messages
- **My Candidates** (read-only): View all candidates assigned to this instructor. Cannot create, edit, or delete candidates. Can see: name, category, phone, registration date, practical hours completed/total, payment status
- **Calendar**: Interactive calendar for managing practical lesson scheduling
  - View scheduled lessons by day/week/month
  - Request new lesson slots (pending admin approval or auto-approved based on tenant settings)
  - Mark lessons as completed → auto-creates practical_hour_sessions record
  - Cancel lessons with reason
  - Color-coded by status: scheduled (blue), completed (green), cancelled (red), no-show (orange)
- **Debt Dashboard**: Shows 65€ charge per assigned candidate
  - Total candidates assigned, total amount owed, total paid, remaining balance
  - Payment history table
  - Per-candidate breakdown
- **Messages**: Communication channel with school admins
  - Threaded conversations
  - New message to admin
  - Read/unread indicators
  - Real-time updates (polling or WebSocket)

**Instructor Payment Economics**:
- When a candidate is assigned to an instructor, an `instructor_payments` record is auto-created with amount = `instructor.cost_per_candidate` (default 65€)
- Admins can record payments from instructors
- Instructor dashboard shows running debt balance
- Admin dashboard shows aggregate instructor debt

#### API Endpoints
```
# Admin Instructor Management
GET    /api/v1/instructors                    # List with filters
POST   /api/v1/instructors                    # Create (with email+password → auto-creates user)
GET    /api/v1/instructors/{id}               # Get instructor details
PUT    /api/v1/instructors/{id}               # Update instructor
DELETE /api/v1/instructors/{id}               # Deactivate instructor
GET    /api/v1/instructors/{id}/candidates    # Active candidates for instructor

# Instructor Debt Tracking
GET    /api/v1/instructors/{id}/payments      # Payment history for instructor
POST   /api/v1/instructors/{id}/payments      # Record instructor payment (admin)
GET    /api/v1/instructors/{id}/debt-summary  # Debt summary (total, paid, balance)

# Calendar / Scheduling
GET    /api/v1/scheduled-lessons              # List (filterable by instructor, date range, status)
POST   /api/v1/scheduled-lessons              # Schedule a new lesson
GET    /api/v1/scheduled-lessons/{id}         # Get lesson details
PUT    /api/v1/scheduled-lessons/{id}         # Update lesson
DELETE /api/v1/scheduled-lessons/{id}         # Cancel lesson
POST   /api/v1/scheduled-lessons/{id}/complete  # Mark as completed → creates practical_hour_session

# Instructor Self-Service (uses g.current_user to identify instructor)
GET    /api/v1/instructor/me                  # My instructor profile
GET    /api/v1/instructor/candidates          # My assigned candidates (read-only)
GET    /api/v1/instructor/calendar            # My scheduled lessons
GET    /api/v1/instructor/debt                # My debt summary + payment history
GET    /api/v1/instructor/dashboard           # Dashboard stats

# Messaging
GET    /api/v1/conversations                  # List conversations
POST   /api/v1/conversations                  # Start new conversation
GET    /api/v1/conversations/{id}/messages    # Get messages in conversation
POST   /api/v1/conversations/{id}/messages    # Send message
PUT    /api/v1/messages/{id}/read             # Mark message as read
GET    /api/v1/messages/unread-count          # Unread message count
```

---

### MODULE 6: Vehicle Management
**Priority: P1**
**Dependencies: Module 1, Module 5**
**Estimated effort: 1 day**

#### Backend
```
backend/app/
├── models/
│   └── vehicle.py
├── api/
│   └── vehicles.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── vehicles/
│       └── page.tsx             # Vehicle list with CRUD
├── components/
│   └── vehicles/
│       ├── VehicleTable.tsx
│       └── VehicleForm.tsx
```

#### Key Features
- 16+ vehicles with: make, chassis number, plate number, registration dates, technical control date
- Instructor assignment (one vehicle per instructor)
- Registration expiry tracking
- Technical control expiry alerts

#### API Endpoints
```
GET    /api/vehicles
POST   /api/vehicles
PUT    /api/vehicles/{id}
DELETE /api/vehicles/{id}
```

---

### MODULE 7: Candidate Management (Core Module)
**Priority: P0**
**Dependencies: Module 1, Module 2, Module 4, Module 5, Module 6**
**Estimated effort: 3-4 days**

#### Backend
```
backend/app/
├── models/
│   └── candidate.py
├── api/
│   └── candidates.py
├── services/
│   └── candidate_service.py     # Business logic
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── candidates/
│       ├── page.tsx             # Lista - table view with filters & pagination
│       ├── search/page.tsx      # Kerko - card view search
│       ├── archive/page.tsx     # Arkiva - completed candidates
│       ├── supplementary/page.tsx # Ore Plotesuese
│       └── new/page.tsx         # Registration form
├── components/
│   └── candidates/
│       ├── CandidateTable.tsx   # Full table with all columns
│       ├── CandidateCard.tsx    # Card view for search results
│       ├── CandidateForm.tsx    # Registration form (complex!)
│       ├── CandidateFilters.tsx # Category, date range, gender, automatic, search
│       ├── CandidateDetail.tsx  # Detail view with action buttons
│       └── CandidateActions.tsx # Fshi, Edito, Ore Shtese, Paguaj buttons
```

#### Key Features

**Lista (Table View)**:
- Paginated table with columns: Kandidati, Nr. Protokollit, Nr. Personal, Telefoni, Data Regjistrimit, Instruktori, Ore (theory/practical), Paguar, Borxhi
- Filters: Kandidati dropdown, Kategoria, Nga Data, Deri Data, search text, Gjinia, Automatik
- Export: PDF, Excel, Word via `/api/candidates/export?type={pdf|excel|word}`

**Kerko (Search/Card View)**:
- Card-based search results showing candidate details
- Each card shows: full name (category), personal number, phone, email, hours, price, payment status, documents status, registration date, practical hours realized
- Action buttons per candidate: Fshi Komplet, Fshi, Edito, Ore Shtese, Paguaj
- Print buttons: Ore Teorike, Ore praktike, Vertetimi, Fatura, Fletëparaqitja, Libreza, Kontrata, Print Testi

**Registration Form** (complex modal):
- Emri, Emri i Prindit, Mbiemri
- Numri Personal (10 digits), Telefoni, Email
- Shteti/Komuna/Vendi Vendlindja (cascading dropdowns - Country → Municipality → Place)
- Data e lindjes (date picker, format dd.MM.yyyy)
- Gjinia (M/F dropdown)
- Komuna/Vendbanimi (residence, separate cascading dropdowns)
- Kategoria (B/CE/C/D), Automatik checkbox
- Cmimi (price, auto-filled from category), Shuma e Paguar
- Ore Praktike, Ore Teorike (defaults from category)
- Data e Regjistrimit, Numri Rendor
- Medical certificate: checkbox + number + date
- Document checkboxes: Vertetimi, Cert. Kryqi Kuq, Leternjoftimi
- Ligjeruesi, Instruktori, Automjeti dropdowns
- Komente (comments textarea)

**Arkiva (Archive)**: Same search as Kerko but only for completed/archived candidates

**Ore Plotesuese (Supplementary Hours)**: Candidates needing extra hours - separate registration

#### API Endpoints
```
GET    /api/candidates                    # List with filters & pagination
POST   /api/candidates                    # Create new candidate
GET    /api/candidates/{id}               # Get candidate details
PUT    /api/candidates/{id}               # Update candidate
DELETE /api/candidates/{id}               # Soft delete (fshi)
DELETE /api/candidates/{id}/complete       # Full delete (fshi komplet)
POST   /api/candidates/{id}/archive       # Move to archive
GET    /api/candidates/search             # Card-view search
GET    /api/candidates/archive            # Archived candidates
GET    /api/candidates/supplementary      # Candidates with extra hours
POST   /api/candidates/{id}/supplementary # Register extra hours
GET    /api/candidates/export?type={type} # Export PDF/Excel/Word
```

---

### MODULE 8: Theory Hours Management
**Priority: P1**
**Dependencies: Module 7**
**Estimated effort: 1-2 days**

#### Backend
```
backend/app/
├── models/
│   └── theory_session.py
├── api/
│   └── theory_hours.py
├── services/
│   └── theory_service.py
```

#### Frontend
```
frontend/components/
└── candidates/
    ├── TheoryHoursModal.tsx      # 8-row table with chapter groupings
    └── TheoryEvidenceModal.tsx   # Bulk theory hours management
```

#### Key Features
- Per-candidate theory hour tracking with 8 sessions (for category B)
- Each session: chapter topics (pre-defined groupings like "1.1, 1.2, 1.3"), date, time from/to, hours count, realized checkbox
- Chapter groupings per category:
  - Session 1: 1.1, 1.2, 1.3
  - Session 2: 1.4, 1.5, 1.6
  - Session 3: 2.1, 2.2, 2.3
  - Session 4: 3.1, 3.2, 3.3, 3.4
  - Session 5: 4.1, 4.2
  - Session 6: 5.1, 5.2, 5.3
  - Session 7: 6.1, 6.2, 7.1, 7.2
  - Session 8: 8.1, 8.2, 8.3, 9.1, 9.2, 9.3
- Default times: 16:00-17:30, 2 hours each
- Total hours counter (auto-calculated)
- **Evidenca Oreve**: Bulk management modal - select category + chapter + date, shows all candidates for that session, mark realized in bulk

#### API Endpoints
```
GET    /api/candidates/{id}/theory-hours       # Get theory sessions
PUT    /api/candidates/{id}/theory-hours       # Save/update all sessions
GET    /api/theory-evidence                     # Bulk: candidates for a session
PUT    /api/theory-evidence                     # Bulk: mark sessions realized
```

---

### MODULE 9: Practical Hours Management
**Priority: P1**
**Dependencies: Module 7, Module 5**
**Estimated effort: 1-2 days**

#### Backend
```
backend/app/
├── models/
│   └── practical_session.py
├── api/
│   └── practical_hours.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── candidates/
│       └── practical-hours/page.tsx  # Oret praktike list page
├── components/
│   └── candidates/
│       └── PracticalHourModal.tsx    # Add practical hour session
```

#### Key Features
- Log individual practical driving sessions per candidate
- Fields: client (pre-selected), instructor (dropdown), date, time, number of hours, price per hour, remarks
- List view: search by candidate, instructor, paid status
- Kerko kliente button to find candidates
- Payment tracking per session

#### API Endpoints
```
GET    /api/candidates/{id}/practical-hours      # Get sessions for candidate
POST   /api/candidates/{id}/practical-hours      # Add practical hour session
PUT    /api/practical-hours/{id}                  # Update session
DELETE /api/practical-hours/{id}                  # Delete session
GET    /api/practical-hours                       # List all (with filters)
```

---

### MODULE 10: Payment Management
**Priority: P1**
**Dependencies: Module 7**
**Estimated effort: 1-2 days**

#### Backend
```
backend/app/
├── models/
│   └── payment.py
├── api/
│   └── payments.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── candidates/
│       └── payments/page.tsx
├── components/
│   └── payments/
│       ├── PaymentForm.tsx         # Paguaj modal
│       └── PaymentList.tsx         # Payments search page
```

#### Key Features
- Register payments for candidates (Paguaj button on candidate card)
- Payment search with filters: Kategoria, Menyra e pageses (method), Kandidati, Kryer nga (received by), date range, Paguar status, Ore Plotesuese flag
- Payment methods tracking
- Auto-calculate debt (Borxhi = Cmimi - total payments)
- Lista me Kandidat button for candidate-grouped payment view
- Track supplementary vs regular payments separately

#### API Endpoints
```
GET    /api/payments                    # List with filters
POST   /api/payments                    # Register payment
GET    /api/payments/{id}
PUT    /api/payments/{id}
DELETE /api/payments/{id}
GET    /api/candidates/{id}/payments    # Payments for specific candidate
```

---

### MODULE 11: Verification (Vërtetim) Management
**Priority: P1**
**Dependencies: Module 7, Module 8, Module 9**
**Estimated effort: 1-2 days**

#### Backend
```
backend/app/
├── models/
│   └── verification.py
├── api/
│   └── verifications.py
```

#### Frontend
```
frontend/components/
└── candidates/
    └── VerificationForm.tsx     # Registration modal
```

#### Key Features
- Create verification records for candidates
- Required data: verification date, theory hours start/end dates, practical hours start/end dates, sequence number, lecturer, instructor, Red Cross cert, ID copy
- Pre-filled candidate and category info
- Must have theory + practical hours data before creating (as user noted)
- Triggers Vërtetim PDF generation

#### API Endpoints
```
GET    /api/candidates/{id}/verification          # Get verification
POST   /api/candidates/{id}/verification          # Create verification
PUT    /api/candidates/{id}/verification/{vid}    # Update
```

---

### MODULE 12: Expense Management
**Priority: P2**
**Dependencies: Module 1, Module 6**
**Estimated effort: 1-2 days**

#### Backend
```
backend/app/
├── models/
│   ├── expense.py
│   └── expense_type.py
├── api/
│   ├── expenses.py
│   └── expense_types.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── expenses/
│       ├── page.tsx             # Expense list with filters
│       └── types/page.tsx       # Expense type management
├── components/
│   └── expenses/
│       ├── ExpenseTable.tsx
│       └── ExpenseForm.tsx      # Registration modal
```

#### Key Features
- Expense registration: vehicle/type, date, amount, description
- Expense type CRUD (Lloji i shpenzimeve)
- Reporting: filter by report type (monthly), year, month, expense type
- Vehicle-linked expenses

#### API Endpoints
```
GET    /api/expenses                     # List with filters
POST   /api/expenses
PUT    /api/expenses/{id}
DELETE /api/expenses/{id}
GET    /api/expense-types
POST   /api/expense-types
PUT    /api/expense-types/{id}
DELETE /api/expense-types/{id}
```

---

### MODULE 13: User Management
**Priority: P1**
**Dependencies: Module 1**
**Estimated effort: 1 day**

#### Backend
```
backend/app/
├── api/
│   └── users.py
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   └── admin/
│       └── users/
│           └── page.tsx
├── components/
│   └── admin/
│       └── UserForm.tsx
```

#### Key Features
- List users for tenant: username, role, full name, personal number, email, creation date, active status
- CRUD operations (admin only)
- Password reset functionality
- Role assignment: Administrator
- Activation/deactivation

#### API Endpoints
```
GET    /api/users
POST   /api/users
PUT    /api/users/{id}
DELETE /api/users/{id}
POST   /api/users/{id}/reset-password
PUT    /api/users/{id}/toggle-active
```

---

### MODULE 14: PDF Document Generation (Critical Module)
**Priority: P0**
**Dependencies: Module 7, Module 8, Module 9, Module 11**
**Estimated effort: 4-5 days**

#### Backend
```
backend/app/
├── pdf/
│   ├── __init__.py
│   ├── generator.py             # WeasyPrint PDF engine
│   ├── templates/
│   │   ├── base.html            # Shared PDF base template
│   │   ├── fatura.html          # Invoice
│   │   ├── fleteparaqitja.html  # Submission form (2 pages)
│   │   ├── libreza.html         # Candidate booklet (2 pages)
│   │   ├── kontrata.html        # Contract (1 page)
│   │   ├── vertetimi.html       # Verification certificate (1 page)
│   │   ├── testi.html           # Test print (4 pages)
│   │   └── kandidatet_lista.html # Candidate list export
│   ├── styles/
│   │   └── pdf_styles.css       # Shared PDF styling
│   └── assets/
│       ├── kosovo_coat_of_arms.png
│       └── school_logo.png
├── api/
│   └── print.py                 # PDF generation endpoints
```

#### Frontend
```
frontend/components/
└── candidates/
    └── PrintButtons.tsx         # Row of colored print action buttons
```

#### Document Specifications

**1. Fatura (Invoice)** - `PrintFaturaKandidati`
- School branding header (name, NUI, TVSH, address, phone, email)
- Invoice number and date
- Candidate info: name, personal number, address
- Service line items table with VAT calculation
- Bank account details (TEB, account number)
- 1 page

**2. Fletëparaqitja (Submission Form)** - `PrintFleteparaqitja`
- Kosovo Republic coat of arms header
- Official government form layout
- Candidate personal details
- Category highlighting (B/C/D/CE)
- Documents checklist (medical cert, Red Cross, ID)
- Theory test results table
- Signature fields
- 2 pages

**3. Libreza (Candidate Booklet)** - `PrintKandidatiLibreza`
- Page 1: Practical driving log table (20 rows: date, time, plates, topic, signatures)
- Page 2: Personal info card with individual character boxes for personal number
- School stamp area
- 2 pages

**4. Kontrata (Contract)** - `PrintKandidatiKontrata`
- Legal contract title: "KONTRATË PËR AFTËSIMIN E KANDIDATIT PËR SHOFER"
- Date, school info, candidate info
- 9 numbered articles (I-IX) covering:
  - Training objective and category
  - Legal references (Udhëzimit Administrativ Nr. 13/2017, Ligjin Nr. 05/L-064)
  - Theory hours (count, price per hour: 2.08 EUR for B)
  - Practical hours (count, price per hour: 7.92 EUR for B)
  - Bank details
  - Termination clauses
  - Age requirement (18+)
  - Dispute resolution (Ferizaj court)
- Dual signature fields: KANDIDATI and Autoshkolla
- 1 page

**5. Vërtetimi (Verification Certificate)** - `PrintKandidatiVertetimi`
- School header with license number
- Title: "V Ë R T E T I M"
- Candidate details with character boxes for personal number
- Theory hours: subject, hours count, from date, to date
- Practical hours: subject, hours count, from date, to date
- Lecturer and instructor name/signature fields
- Director signature and stamp area (v.v)
- Date of issuance
- 1 page

**6. Print Testi (Test Print)** - `PrintTestiKandidati`
- Header: "Test provues [number]", candidate name, score, category
- Multiple choice questions with traffic situation images
- Answer options (A/B/C) with correct answers in green checkmarks, wrong in red
- Points per question (4 Pikë each)
- Traffic sign images alongside questions
- 4 pages

**7. Kandidatet Lista (Candidate List Export)** - `PrintKandidatetLista`
- Table format matching the Lista view
- Export types: PDF, Excel (.xlsx), Word (.docx)
- All filter criteria applied

#### API Endpoints
```
GET /api/print/fatura?candidate_id={id}&type=pdf
GET /api/print/fleteparaqitja?candidate_id={id}&category={cat}&type=pdf
GET /api/print/libreza?candidate_id={id}&category={cat}&type=pdf
GET /api/print/kontrata?candidate_id={id}&category={cat}&type=pdf
GET /api/print/vertetimi?candidate_id={id}&category={cat}&type=pdf
GET /api/print/testi?candidate_id={id}&category={cat}&type=pdf
GET /api/print/candidates-list?type={pdf|excel|word}&filters...
```

---

### MODULE 15: Super-Admin Panel
**Priority: P1**
**Dependencies: Module 1**
**Estimated effort: 2-3 days**

#### Backend
```
backend/app/
├── api/
│   └── superadmin.py
├── models/
│   └── audit_log.py
```

#### Frontend
```
frontend/app/
├── (superadmin)/
│   ├── layout.tsx               # Super-admin layout
│   ├── page.tsx                 # Dashboard with stats
│   ├── tenants/
│   │   ├── page.tsx             # All driving schools
│   │   └── [id]/page.tsx        # Tenant detail + impersonate
│   └── audit/page.tsx           # Audit log viewer
├── components/
│   └── superadmin/
│       ├── TenantTable.tsx
│       ├── ImpersonationBanner.tsx
│       └── AuditLog.tsx
```

#### Key Features
- Dashboard with global stats (total schools, candidates, revenue)
- Tenant CRUD: create/edit/deactivate driving schools
- Impersonate any user in any tenant
- Audit log of all actions across tenants
- Billing/subscription management (future)

#### API Endpoints
```
GET    /api/superadmin/tenants
POST   /api/superadmin/tenants
GET    /api/superadmin/tenants/{id}
PUT    /api/superadmin/tenants/{id}
DELETE /api/superadmin/tenants/{id}
GET    /api/superadmin/stats
GET    /api/superadmin/audit-log
POST   /api/auth/impersonate      # (from Module 1)
```

---

### MODULE 16: Dashboard & Layout
**Priority: P1**
**Dependencies: Module 1**
**Estimated effort: 3-4 days**

#### Backend
```
backend/app/
├── api/
│   └── dashboard.py             # Dashboard stats endpoints
├── services/
│   └── dashboard_service.py     # Dashboard data aggregation
```

#### Frontend
```
frontend/app/
├── (dashboard)/
│   ├── layout.tsx               # Main admin dashboard layout
│   ├── page.tsx                 # Admin dashboard home (fantastic dashboard!)
│   └── settings/page.tsx        # School settings
├── (instructor)/
│   ├── layout.tsx               # Instructor portal layout
│   └── page.tsx                 # Instructor dashboard home
├── components/
│   ├── layout/
│   │   ├── AdminSidebar.tsx     # Admin collapsible sidebar
│   │   ├── InstructorSidebar.tsx # Instructor simplified sidebar
│   │   ├── Header.tsx           # Top bar: school name, user menu, session timer
│   │   └── Footer.tsx           # Session timer: "Kyçja: DD.MM.YYYY HH:MM:SS Aktive edhe: XX min."
│   ├── dashboard/
│   │   ├── AdminDashboard.tsx   # Admin dashboard with all widgets
│   │   ├── StatsCard.tsx        # Metric card component
│   │   ├── RevenueChart.tsx     # Revenue over time chart
│   │   ├── CandidatesByCategory.tsx  # Donut chart
│   │   ├── InstructorDebtSummary.tsx # Instructor payment overview
│   │   ├── RecentActivity.tsx   # Activity feed
│   │   ├── TodaySchedule.tsx    # Today's lessons schedule
│   │   ├── ExpiringDocuments.tsx # Expiring licenses/registrations
│   │   └── InstructorDashboard.tsx  # Instructor dashboard widgets
│   └── shared/
│       ├── DataTable.tsx        # Reusable sortable/filterable table
│       ├── Modal.tsx            # Reusable modal component
│       ├── DatePicker.tsx       # dd.MM.yyyy format
│       ├── CascadingDropdown.tsx # Country → Municipality → Place
│       ├── ExportButtons.tsx    # PDF/Excel/Word export
│       ├── FilterBar.tsx        # Reusable filter bar
│       └── Calendar.tsx         # Reusable calendar component
```

#### Admin Dashboard (Fantastic Dashboard for Each Driving School)

The admin dashboard is the first thing administrators see when they log in. It must be visually impressive, informative, and actionable.

**Top Row — Key Metrics (4 cards)**:
- Kandidatë Aktive (Active Candidates): count + trend vs last month
- Të Ardhurat Mujore (Monthly Revenue): total € collected this month + trend
- Orë Praktike Sot (Practical Hours Today): scheduled lessons count
- Borxhi i Instruktorëve (Instructor Debt): total outstanding from all instructors

**Second Row — Charts (2 columns)**:
- Left: Revenue chart (line/bar) — last 6 months, showing revenue collected vs target
- Right: Candidates by Category (donut chart) — B, C, CE, D breakdown

**Third Row — Tables/Feeds (2 columns)**:
- Left: Today's Schedule — upcoming practical lessons with instructor, candidate, time, vehicle
- Right: Recent Activity feed — last 10 actions (new registrations, payments received, lessons completed)

**Fourth Row — Alerts & Status**:
- Expiring vehicle registrations (within 30 days)
- Expiring school licenses (within 60 days)
- Candidates with overdue payments (borxhi > 0 for 30+ days)
- Instructors with high debt balance

**Dashboard API Endpoints**:
```
GET /api/v1/dashboard/stats           # Key metrics (candidates, revenue, hours, debt)
GET /api/v1/dashboard/revenue-chart   # Revenue data for charts (monthly)
GET /api/v1/dashboard/category-breakdown  # Candidates per category
GET /api/v1/dashboard/today-schedule  # Today's scheduled lessons
GET /api/v1/dashboard/recent-activity # Latest activity feed
GET /api/v1/dashboard/alerts          # Expiring docs, overdue payments, etc.
```

#### Instructor Dashboard

A simplified, focused dashboard for instructors showing only what they need.

**Top Row — Key Metrics (4 cards)**:
- Kandidatët e Mi (My Candidates): active assigned candidates count
- Mësimet Sot (Today's Lessons): scheduled lessons today
- Borxhi Im (My Debt): total outstanding balance (€)
- Mesazhe të Pa-lexuara (Unread Messages): count with link

**Second Row**:
- Left: This Week's Calendar — visual weekly calendar with lessons
- Right: My Candidates list (quick view with names, category, hours progress)

**Third Row**:
- Payment history — recent payments and remaining debt per candidate

#### Admin Sidebar Structure
```
├── Paneli (Dashboard)
├── Auto Shkolla
│   ├── Profili (School details)
│   └── Licensat (Licenses)
├── Instruktor / Ligjerues
│   ├── Lista (Instructors)
│   └── Pagesat e Instruktorëve (Instructor Payments)
├── Automjetet
│   └── Lista (Vehicles)
├── Kandidatet
│   ├── Lista (Table view)
│   ├── Kerko (Card search)
│   ├── Ore Plotesuese (Supplementary)
│   ├── Arkiva (Archive)
│   ├── Pagesat (Payments)
│   ├── Oret praktike (Practical hours)
│   ├── Evidenca Oreve (Hours evidence)
│   └── Evidenca (Evidence)
├── Kalendari (Calendar/Schedule)
├── Shpenzimet
│   ├── Lista (Expenses)
│   └── Lloji (Expense types)
├── Mesazhet (Messages)
├── Administrimi
│   ├── Kategorite (Categories)
│   └── Perdoruesit (Users)
└── Kontakti (Contact)
```

#### Instructor Sidebar Structure
```
├── Paneli (Dashboard)
├── Kandidatët e Mi (My Candidates — read-only)
├── Kalendari (Calendar)
├── Pagesat (My Debt/Payments)
├── Mesazhet (Messages)
└── Profili Im (My Profile)
```

---

## 5. Development Order & Dependencies

```
Phase 1 (Foundation - Week 1):
  Module 1: Auth & Multi-tenancy ──┐
  Module 2: Location Data ─────────┤
  Module 16: Dashboard & Layout ────┘

Phase 2 (Core Config - Week 1-2):
  Module 4: Categories ────────────┐
  Module 5: Instructors ───────────┤  (can be parallel)
  Module 6: Vehicles ──────────────┤
  Module 3: School Profile ────────┘

Phase 3 (Main Features - Week 2-3):
  Module 7: Candidate Management ──┐
  Module 13: User Management ──────┘  (can be parallel)

Phase 4 (Candidate Features - Week 3-4):
  Module 8: Theory Hours ──────────┐
  Module 9: Practical Hours ───────┤  (can be parallel)
  Module 10: Payments ─────────────┤
  Module 11: Verification ─────────┤
  Module 12: Expenses ─────────────┘

Phase 5 (Documents & Admin - Week 4-5):
  Module 14: PDF Generation ───────┐
  Module 15: Super-Admin Panel ────┘  (can be parallel)
```

---

## 6. Project Structure

```
autoshkolla-pro/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Config (dev/staging/prod)
│   │   ├── models/              # All SQLAlchemy models
│   │   ├── api/                 # All API route blueprints
│   │   ├── schemas/             # Request/response validation schemas
│   │   ├── services/            # Business logic layer
│   │   ├── middleware/          # Auth, tenant context, audit
│   │   ├── pdf/                 # PDF templates & generator
│   │   ├── utils/               # DB, JWT, helpers, validators
│   │   └── seeds/               # Database seed scripts
│   ├── migrations/              # Alembic migrations
│   ├── tests/                   # Pytest tests
│   ├── requirements.txt
│   ├── wsgi.py                  # Entry point (runs on port 5002)
│   └── .env.example
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   ├── components/              # React components
│   ├── lib/                     # API client, auth, types
│   ├── hooks/                   # Custom React hooks
│   ├── public/                  # Static assets
│   ├── styles/                  # Global styles
│   ├── package.json
│   ├── next.config.js
│   └── .env.local
├── .env.example
├── DEVELOPMENT_PLAN.md          # This file
└── README.md
```

---

## 7. Environment Setup

```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python wsgi.py  # Runs on port 5002

# Frontend Setup (in another terminal)
cd frontend
npm install
npm run dev  # Runs on port 3000

# Services:
# - Flask API: localhost:5002
# - Next.js: localhost:3000
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://autoshkolla:dev_password@localhost:5432/autoshkolla_pro
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Super Admin
SUPER_ADMIN_EMAIL=admin@autoshkolla-pro.com
SUPER_ADMIN_PASSWORD=initial-password

# PDF
WEASYPRINT_FONT_DIR=/app/fonts
```

---

## 8. Key Implementation Notes

### Multi-tenancy Pattern
Every model with tenant-scoped data includes `tenant_id`. A Flask middleware (`tenant_context.py`) extracts the tenant from the JWT token and sets `g.tenant_id`. All SQLAlchemy queries are automatically filtered:

```python
class TenantMixin:
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)

    @classmethod
    def query_for_tenant(cls):
        return cls.query.filter_by(tenant_id=g.tenant_id)
```

### Cascading Dropdowns
The Country → Municipality → Place pattern requires three API calls chained on the frontend:
1. Load countries on mount
2. On country select → load municipalities
3. On municipality select → load places

### PDF Generation Strategy
Use WeasyPrint with Jinja2 HTML templates. Each PDF type has an HTML template that closely mirrors the current system's layout. The templates use CSS for precise positioning (especially for character boxes in Libreza and Vërtetim).

### Albanian Date Format
All dates throughout the system use `dd.MM.yyyy` format (e.g., 09.03.2026). The frontend DatePicker component must enforce this format.

### Session Timer
The current system shows "Aktive edhe: 60 min" with countdown. Implement via JWT token expiry + frontend countdown timer that refreshes the token before expiry.

---

## 9. Parallel Agent Assignment Guide

Each module can be assigned to a separate agent. Here's how to brief each agent:

| Agent | Module(s) | Brief |
|-------|-----------|-------|
| Agent A | 1 + 2 | "Set up Flask backend with JWT auth, multi-tenancy middleware, and seed Kosovo location data" |
| Agent B | 16 | "Create Next.js frontend shell: dashboard layout, sidebar, shared components (DataTable, Modal, DatePicker, CascadingDropdown)" |
| Agent C | 3 + 4 + 5 + 6 | "Build school profile, categories, instructors, and vehicles CRUD (simple entity management)" |
| Agent D | 7 | "Build the candidate management module - the core entity with complex registration form, list/search/archive views" |
| Agent E | 8 + 9 + 10 + 11 | "Build candidate-related features: theory hours, practical hours, payments, and verification management" |
| Agent F | 14 | "Build PDF generation: 7 document types using WeasyPrint, matching exact layouts from the original system" |
| Agent G | 12 + 13 + 15 | "Build expense management, user management, and super-admin panel" |

Each agent MUST follow this workflow for every change:

1. **Read first**: Read `CLAUDE.md` and this plan before starting
2. **Check dependencies**: Verify dependent modules are complete (check `docs/MODULES_STATUS.md`)
3. **Implement**: Build database models, API routes, and frontend components
4. **Write tests**: Unit tests (pytest) for every model/service/route + Playwright E2E for user flows
5. **Run tests**: `pytest -v --cov=app` — ALL tests must pass before considering done
6. **Update CLAUDE.md**: If you add conventions, patterns, or new setup steps
7. **Update /docs/**:
   - `docs/CHANGELOG.md` — Add dated entry of what you did
   - `docs/MODULES_STATUS.md` — Update completion percentages
   - `docs/API_REFERENCE.md` — Add/update endpoint docs if API changed
   - `docs/DATABASE_SCHEMA.md` — Update if schema changed
   - Create `docs/module-{N}-{name}.md` with detailed notes on what was built, decisions made, and what's left
8. **Follow project conventions**: See `CLAUDE.md` for all rules

---

## 10. Testing Requirements

### Unit Tests (pytest)
- Every model: test creation, validation, relationships, methods
- Every service function: test business logic, edge cases, error handling
- Every API route: test happy path, validation errors, auth, tenant isolation
- Use `factory-boy` for test data factories
- Target: **80%+ code coverage**

### Integration Tests (pytest + Flask test client)
- Test full request/response cycles
- Test multi-tenant isolation (user A can't see user B's data)
- Test role-based access (instructor can't access admin routes)
- Test cascading operations (delete candidate → cleanup related records)

### E2E Tests (Playwright)
- Test every major user flow:
  - Login → Dashboard → Navigate sidebar
  - Create candidate → View → Edit → Delete
  - Register payment → View in payments list
  - Generate PDF → Verify content
  - Super-admin impersonation flow
- Test across different roles
- Test responsive layout

### Running Tests
```bash
# Backend unit + integration
cd backend && pytest -v --cov=app --cov-report=html

# E2E
cd backend && playwright test

# Frontend
cd frontend && npm run test
```

---

## 11. Documentation Protocol

### After EVERY Change
Agents must update these files to maintain context across all agents:

| File | What to update |
|------|---------------|
| `CLAUDE.md` | New conventions, setup steps, patterns |
| `docs/CHANGELOG.md` | Dated entry: what changed, by which module |
| `docs/MODULES_STATUS.md` | Update % complete for affected modules |
| `docs/API_REFERENCE.md` | New/changed endpoints with request/response format |
| `docs/DATABASE_SCHEMA.md` | New/changed tables, columns, indexes |
| `docs/module-{N}-{name}.md` | Detailed implementation notes for the module |

### Why This Matters
- Multiple agents work in parallel on different modules
- Each agent needs to know what other agents have built
- The `/docs/` folder is the **single source of truth** for project state
- Without docs, agents will duplicate work or break dependencies

---

## 12. Multi-tenancy Deep Dive

### How It Works
1. Each driving school (Autoshkollë) is a **tenant** in the `tenants` table
2. Every user belongs to exactly one tenant via `users.tenant_id`
3. Every data table has a `tenant_id` column (except shared reference data)
4. The Flask middleware extracts `tenant_id` from the JWT token on every request
5. All queries are automatically filtered: `WHERE tenant_id = :current_tenant`
6. **A user from Autoshkolla Rina can NEVER see data from Autoshkolla XYZ**

### Super-Admin
- Special role that exists outside any tenant
- Can view ALL tenants and their data
- Can impersonate any user in any tenant (creates a temporary session)
- Impersonation shows a yellow banner: "Po e menaxhoni: [Emri i Autoshkollës] si [Përdoruesi]"
- "Dil nga imitimi" button to return to super-admin view

### Tenant Isolation Checklist
For every new feature, verify:
- [ ] Model has `tenant_id` column
- [ ] All queries use `TenantMixin.query_for_tenant()`
- [ ] API routes have `@require_auth` decorator
- [ ] Tests verify tenant isolation (create data in tenant A, verify not visible from tenant B)
- [ ] No raw SQL queries that bypass tenant filtering
