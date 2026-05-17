# Autoshkolla Platform Architecture Overview

## Project Description

**Autoshkolla Platform** is a comprehensive multi-tenant driving school CRM (Customer Relationship Management) system designed for driving schools in Kosovo. It provides complete management of instructors, candidates, vehicles, theory and practical hours, payments, verifications, and administrative operations.

### Technology Stack
- **Frontend**: Next.js with Albanian UI language support
- **Backend**: Flask with Python (poolgo-ops pattern)
- **Database**: PostgreSQL with multi-tenant architecture
- **PDF Generation**: WeasyPrint + Jinja2 HTML templates
- **Authentication**: PyJWT with custom encode/decode (not Flask-JWT-Extended)
- **Testing**: pytest (unit/integration), Playwright (E2E)

### Key Features
- Multi-tenant support with complete data isolation
- Super-admin dashboard with tenant management and audit logging
- Advanced candidate management (filtering, archiving, supplementary registrations)
- Theory and practical hours tracking
- Payment management and expense tracking
- Automated PDF generation for various documents (contracts, certificates, test results)
- Role-based access control (super-admin, administrator, instructor, lecturer)
- Full audit trail for compliance

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│                    (Next.js Frontend)                       │
│                   Albanian UI Language                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                        │
│              (Flask REST API with JWT Auth)                 │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Auth       │  │   Locations  │  │   School     │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Categories   │  │ Instructors  │  │  Vehicles    │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Candidates  │  │ Theory Hours │  │ Practical    │      │
│  │   Module     │  │   Module     │  │   Hours      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Payments   │  │Verifications │  │   Expenses   │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Users     │  │  Print/PDF   │  │  Super Admin │      │
│  │   Module     │  │   Module     │  │   Module     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬───────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
    ┌─────────────────┐  ┌──────────────────┐
    │   PostgreSQL    │  │  PDF Generation  │
    │   Database      │  │  (WeasyPrint +   │
    │ (Multi-tenant)  │  │    Jinja2)       │
    └─────────────────┘  └──────────────────┘
```

---

## Multi-Tenancy Approach

### Database Strategy: Shared Database with Row-Level Isolation

Autoshkolla Platform implements multi-tenancy through a shared database model with tenant-level data isolation:

#### Key Components

1. **Tenant ID Column**
   - Every data table includes a `tenant_id` foreign key column
   - All queries automatically filter by `tenant_id` to ensure complete data isolation
   - Tenant assignment happens at user creation and cannot be changed
   - Super-admin users can access all tenants through impersonation feature

2. **Middleware Filtering**
   - Authentication middleware extracts `tenant_id` from JWT token
   - Request context stores tenant information throughout request lifecycle
   - All database queries automatically include tenant filter clause
   - API endpoints cannot access or modify data from other tenants
   - Cross-tenant requests are rejected with 403 Forbidden response

3. **Data Isolation**
   - Locations (countries, municipalities, places) are shared across all tenants
   - All business data (candidates, instructors, vehicles, etc.) is tenant-isolated
   - User sessions are tenant-specific
   - Audit logs include tenant information for compliance

4. **Scaling Considerations**
   - Shared database model supports horizontal scaling of application servers
   - Tenant ID indexes ensure query performance across all tables
   - Future migration to database-per-tenant model possible without API changes
   - Current approach suitable for 100+ concurrent tenants

---

## Authentication Flow

### JWT-Based Authentication with Refresh Tokens

```
┌──────────────────────────────────────────────────────────────┐
│                    Initial Login                             │
├──────────────────────────────────────────────────────────────┤
│ 1. Client POST /api/auth/login                              │
│    - Email & Password                                       │
│                                                              │
│ 2. Server validates credentials                             │
│    - Checks user exists & password correct                  │
│    - Retrieves tenant_id from user record                   │
│                                                              │
│ 3. Server generates tokens:                                 │
│    - Access Token (JWT, 15 min expiry)                      │
│    - Refresh Token (DB stored, 7 day expiry)                │
│                                                              │
│ 4. Server sends response:                                   │
│    - access_token, refresh_token, expires_in                │
│    - user_id, tenant_id, role, name                         │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│               Authenticated Requests                         │
├──────────────────────────────────────────────────────────────┤
│ Client includes:                                             │
│ Authorization: Bearer <access_token>                         │
│                                                              │
│ Server middleware:                                           │
│ 1. Validates JWT signature & expiry                          │
│ 2. Extracts user_id, tenant_id, role from token            │
│ 3. Sets request context with tenant info                    │
│ 4. Allows or denies based on role & permissions            │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│          Token Refresh (15 min before expiry)               │
├──────────────────────────────────────────────────────────────┤
│ 1. Client POST /api/auth/refresh                            │
│    - refresh_token in request body                          │
│                                                              │
│ 2. Server validates refresh token:                          │
│    - Checks token exists in database                        │
│    - Confirms not revoked or expired                        │
│    - Verifies matches user record                           │
│                                                              │
│ 3. Server issues new access token                           │
│    - Refresh token rotated (new one issued)                 │
│    - Old token invalidated                                  │
│                                                              │
│ 4. Response: new access_token, new refresh_token            │
└──────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────┐
│         Super-Admin Impersonation (Tenant Switching)        │
├──────────────────────────────────────────────────────────────┤
│ 1. Super-admin POST /api/auth/impersonate                    │
│    - target_tenant_id in request body                       │
│    - Logged in audit_logs with admin_id & target_tenant    │
│                                                              │
│ 2. Server generates temporary access token:                 │
│    - tenant_id set to target_tenant_id                      │
│    - role remains 'super_admin'                             │
│    - is_impersonating flag set to true                      │
│    - audit entry created                                    │
│                                                              │
│ 3. Client receives impersonation token                      │
│    - Can now access target tenant's data                    │
│    - All actions logged with impersonation flag             │
│                                                              │
│ 4. Super-admin POST /api/auth/exit-impersonate              │
│    - Returns to super_admin context                         │
│    - Logs exit action                                       │
└──────────────────────────────────────────────────────────────┘
```

### Token Claims (JWT Payload)

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "tenant_id": "uuid",
  "role": "administrator|instructor|lecturer|super_admin",
  "name": "User Name",
  "is_impersonating": false,
  "iat": 1234567890,
  "exp": 1234569690
}
```

---

## Backend Architecture (poolgo-ops pattern)

### Core Components

The backend follows the **poolgo-ops pattern**, a structured Flask application architecture designed for maintainability and scalability:

1. **Application Factory (`create_app()`)**
   - Single entry point for application initialization
   - Accepts configuration object (development, testing, production)
   - Registers all blueprints, extensions, and middleware
   - Ensures consistent app state across all contexts

2. **Initialization Middleware (`init_*` functions)**
   - `init_extensions()`: Initialize Flask extensions (SQLAlchemy, JWT, Migrate)
   - `init_blueprints()`: Register API route blueprints
   - `init_middleware()`: Register request/response middleware (auth, tenant context, error handling)
   - `init_error_handlers()`: Register custom error handlers
   - Clear separation of concerns during app startup

3. **Single API Blueprint (`api_bp` at `/api/v1`)**
   - All routes grouped under `/api/v1` prefix
   - Sub-blueprints for each module (auth, candidates, payments, etc.)
   - Centralized versioning strategy for API evolution
   - Enables future API v2, v3 without breaking existing clients

4. **Pydantic BaseSchema for Validation**
   - Request/response validation using Pydantic models (not Flask-RESTful)
   - Replaces dataclasses for more robust validation
   - Type-safe request parsing before handler execution
   - Auto-generated OpenAPI/Swagger documentation
   - Clear error messages with field-level validation results

5. **Response Envelope Wrapping**
   - All API responses wrapped in consistent envelope structure
   - Standard format: `{ "success": bool, "data": {...}, "error": {...} }`
   - Enables client-side error handling without parsing HTTP status codes
   - Supports metadata (pagination, timestamps, request IDs)
   - Improves client robustness to API changes

6. **Custom Error Handler Middleware**
   - Centralized error handling for all exceptions
   - Maps domain exceptions to HTTP status codes and error envelopes
   - Logs errors for debugging and monitoring
   - Returns consistent error format across all endpoints
   - Prevents accidental exposure of internal implementation details

---

## PDF Generation Strategy

### Architecture

Autoshkolla Platform generates PDFs using **WeasyPrint** (Python library) with **Jinja2** HTML templates. This approach provides:
- Python-native generation (no external service needed)
- Full control over styling and layout
- Dynamic content generation from database
- Multi-language support (Albanian)
- Server-side rendering with no JavaScript dependencies

### Workflow

```
Request PDF Document
        ↓
Retrieve Data from Database
        ↓
Render Jinja2 Template with Data
    ↓        ↓        ↓
  CSS    HTML    Images
        ↓
WeasyPrint Converts HTML → PDF
        ↓
Return PDF to Client
```

### Document Types Generated

1. **Fatura** (Invoice)
   - Payment invoices for candidates
   - Date, amount, payment method, candidate details

2. **Fleteparaqitja** (Registration Form)
   - Candidate registration document
   - Personal data, categories, instructors assigned

3. **Libreza** (Logbook)
   - Theory and practical hours summary
   - Chronological entry of completed hours
   - Signed by instructor/lecturer

4. **Kontrata** (Contract)
   - Student-school contract
   - Terms, prices, instructor assignments
   - Legal document requiring signature

5. **Vertetimi** (Certificate)
   - Completion certificate
   - Issued upon successful completion
   - School seal and signature

6. **Testi** (Test Result)
   - Theory test results
   - Score, date, questions answered
   - Pass/fail status

7. **Candidate List**
   - Batch export of all candidates
   - Filters by category, status, date range
   - Summary statistics

### Implementation Details

- Templates stored in `/app/templates/pdfs/`
- Each document type has dedicated template: `{document_type}_al.html`
- Styles included inline or via CSS file: `/app/static/css/pdf-styles.css`
- Dynamic image assets (school logo, watermarks) embedded as base64
- Font embedding for proper rendering of Albanian characters
- Page breaks and headers/footers managed via CSS

---

## Testing Strategy

### Approach: Mandatory Testing with Every Change

All code changes must include corresponding tests. Testing is a non-negotiable part of the development workflow.

### Testing Pyramid

```
        ╱╲
       ╱  ╲    E2E Tests (Playwright)
      ╱────╲   10% coverage
     ╱      ╲  User workflows, critical paths
    ╱────────╲
   ╱          ╲   Integration Tests (pytest)
  ╱────────────╲  30% coverage
 ╱              ╲  API endpoints, database interactions
╱────────────────╲ 60% coverage
Unit Tests (pytest) Module functions, utility logic
```

### Unit Tests (pytest)

**Scope**: Individual functions, business logic, utilities

**Requirements**:
- Minimum 80% code coverage for core modules
- Test happy path, error cases, edge cases
- Use pytest fixtures for common setup
- Mock external dependencies (database, filesystem)
- Tests must run in < 1 second per test

**Structure**:
```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_candidates.py
│   ├── test_payments.py
│   └── ... (one file per module)
└── conftest.py (shared fixtures)
```

**Example Coverage**:
- Input validation (valid, invalid, boundary values)
- Business logic (calculations, state transitions)
- Error handling (exceptions, edge cases)
- Utility functions (string manipulation, formatting)

### Integration Tests (pytest)

**Scope**: API endpoints, database interactions, multi-module workflows

**Requirements**:
- Test full request-response cycle
- Use temporary test database
- Verify database state changes
- Test multi-tenant isolation
- Test permission/authorization
- Tests must run in < 2 seconds per test

**Structure**:
```
tests/
└── integration/
    ├── test_auth_api.py
    ├── test_candidates_api.py
    ├── test_candidates_with_payments.py
    └── ... (one file per module/workflow)
```

**Example Scenarios**:
- Create candidate → Get candidate → Update candidate → Delete candidate
- Create candidate → Add theory hours → Generate logbook PDF
- Login → Create candidate → Logout → Login with different user → Verify isolation
- Super-admin login → Impersonate tenant → Create candidate → Exit impersonate → Verify audit log

### End-to-End Tests (Playwright)

**Scope**: Complete user workflows in browser, UI validation, cross-browser

**Requirements**:
- Test critical user paths only (10% of scenarios)
- Use staging environment or test server
- Verify visual layout and UI interactions
- Test authentication flows end-to-end
- Tests can take 10+ seconds (slower than unit/integration)

**Structure**:
```
tests/
└── e2e/
    ├── test_login_workflow.spec.ts
    ├── test_candidate_creation_workflow.spec.ts
    └── ... (critical user paths only)
```

**Critical Paths**:
- User login → Dashboard → Create candidate → Assign instructor → Print logbook
- User login → View candidates → Filter by category → Export to PDF
- Super-admin login → Switch tenant → Create school profile → View candidates

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific module
pytest tests/unit/test_candidates.py

# With coverage report
pytest --cov=app tests/

# E2E tests
npx playwright test

# E2E with specific browser
npx playwright test --project=chromium
```

### Test Data Management

- Use pytest fixtures in `tests/conftest.py` for common test data
- Create factory functions for generating valid test objects
- Database fixtures auto-rollback changes after each test
- Seed test database with necessary reference data (countries, municipalities)

### CI/CD Integration

- All tests must pass before merge to main branch
- Coverage reports generated for each PR
- E2E tests run on staging environment post-deployment
- Failed tests block deployment to production

---

## Key Design Decisions

### 1. Multi-Tenant Shared Database vs. Database-Per-Tenant

**Decision**: Shared database with tenant_id filtering

**Rationale**:
- Simpler operational overhead (one database to manage)
- Easier tenant onboarding (no new database provisioning)
- Shared reference data (countries, municipalities) across tenants
- Scalable to 100+ tenants with proper indexing
- Future migration to database-per-tenant possible without API changes

**Trade-offs**:
- Requires vigilant tenant isolation in code (middleware enforcement)
- Complex migration path if needed later
- Query performance depends on index quality

---

### 2. JWT with Refresh Tokens vs. Session-Based Auth

**Decision**: JWT with separate refresh tokens stored in database

**Rationale**:
- Stateless authentication (easy horizontal scaling)
- Can revoke tokens by deleting from database
- Refresh token rotation prevents token reuse attacks
- Clear separation: short-lived access token, long-lived refresh token
- Mobile-friendly (no cookies needed)

**Trade-offs**:
- Refresh token rotation adds complexity
- Database query required for refresh (not fully stateless)
- Cannot instantly revoke access tokens (by design for performance)

---

### 3. Super-Admin Impersonation for Multi-Tenant Support

**Decision**: Super-admin can impersonate any tenant's context, all actions logged

**Rationale**:
- Enables support/debugging without creating temp accounts
- Complete audit trail of admin actions in target tenant
- Super-admin remains super-admin role (cannot escalate to admin within tenant)
- Non-invasive troubleshooting
- Compliance: every impersonation logged with timestamps

**Trade-offs**:
- Requires strong access control to super-admin accounts
- Audit log can become large with frequent impersonations
- Potential for misuse if super-admin account compromised

---

### 4. WeasyPrint + Jinja2 for PDF Generation

**Decision**: Server-side PDF generation using WeasyPrint and Jinja2

**Rationale**:
- Python-native solution (no external service dependency)
- Fast rendering (synchronous, no queue needed for typical volumes)
- Full control over styling and fonts (Albanian character support)
- Template reusability and version control
- Works with existing Flask infrastructure

**Trade-offs**:
- Rendering blocks request (mitigated by fast execution)
- Large PDFs could timeout (implement queue for very large batches)
- Requires fonts installed on server for proper rendering
- Learning curve for WeasyPrint CSS limitations

---

### 5. Mandatory Testing with Every Change

**Decision**: All code changes must include corresponding tests (not optional)

**Rationale**:
- Catches regressions early before production
- Documents expected behavior through tests
- Enables safe refactoring
- Reduces QA burden
- Maintains code quality and reliability

**Trade-offs**:
- Slower initial development (faster long-term)
- Developers must write tests (requires discipline)
- Test maintenance burden as code evolves
- CI/CD complexity to enforce test coverage

---

### 6. Role-Based Access Control with Four Roles

**Decision**: Four discrete roles (super_admin, administrator, instructor, lecturer)

**Rationale**:
- Clear permission boundaries
- Instructor and lecturer separation for theory vs. practical distinction
- Administrator per-tenant control
- Super-admin for platform-level management
- Prevents privilege creep

**Trade-offs**:
- Less flexible than attribute-based access control
- Adding new roles requires database migration
- Permission matrices must be explicitly coded

---

### 7. Candidates Module Complexity

**Decision**: Candidates can have multiple categories, instructors, vehicles per course

**Rationale**:
- Real-world driving school operations support multiple training paths
- Candidate can be "suspended" (archived) without deletion
- Supplementary registrations for additional training
- Payment history attached to candidate
- Verification status tracked separately from training

**Trade-offs**:
- Increased database complexity
- More validation rules needed
- Candidate state transitions more complex

---

## Compliance and Governance

- **Data Privacy**: GDPR-aligned (can delete candidates, anonymize records)
- **Audit Trail**: All administrative actions logged with timestamp, user, tenant
- **Multi-Language**: Albanian UI with extensible architecture for other languages
- **Backup Strategy**: Database backups required, PDF exports for compliance
- **Performance**: Target <200ms API response time, <5s PDF generation

---

## Deployment Architecture

- **Backend**: Flask application running in Python venv on port 5002 (python wsgi.py)
- **Frontend**: Next.js dev server on port 3000 (npm run dev)
- **Database**: Managed PostgreSQL with automated backups
- **PDF Generation**: Runs in main application (can be offloaded to separate worker queue if needed)
- **Monitoring**: Application logs, database query logs, audit logs for compliance

