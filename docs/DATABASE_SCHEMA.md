# AutoShkolla Platform - Database Schema

## Overview
PostgreSQL database with multi-tenant architecture. All tenant-scoped tables include a `tenant_id` foreign key. Reference data (locations) is shared across tenants.

**Primary Key Strategy**: UUID (v4) for all tables — compatible with Supabase migration later.

---

## Entity Relationship Summary

```
tenants ──┬── users
          ├── categories
          ├── licenses
          ├── instructors ──┬── vehicles
          │    (has user_id) ├── instructor_payments
          │                  └── scheduled_lessons
          ├── candidates ──┬── theory_hour_sessions
          │                ├── practical_hour_sessions
          │                ├── supplementary_registrations
          │                ├── verifications
          │                ├── payments
          │                └── candidate_tests
          ├── conversations ── messages
          ├── expense_types ── expenses
          └── audit_logs

countries ── municipalities ── places  (shared reference data)
```

---

## Tables

### 1. Shared Reference Data (No tenant_id)

#### countries
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Kosovë, Jasht Kosovës |
| code | VARCHAR(10) | UNIQUE | KS, OTHER |
| created_at | TIMESTAMP | DEFAULT NOW() | |

#### municipalities
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| country_id | UUID | FK → countries.id, NOT NULL | |
| name | VARCHAR(100) | NOT NULL | Ferizaj, Prishtinë, etc. |
| code | INTEGER | UNIQUE | Legacy ID mapping (Ferizaj=3) |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_municipalities_country_id` on `country_id`

#### places
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| municipality_id | UUID | FK → municipalities.id, NOT NULL | |
| name | VARCHAR(200) | NOT NULL | Village/city name |
| code | INTEGER | | Legacy ID mapping (Ferizaj city=205) |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_places_municipality_id` on `municipality_id`

---

### 2. Authentication & Tenancy

#### tenants
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| name | VARCHAR(200) | NOT NULL | "Autoshkolla Rina" |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | "autoshkolla-rina" (for URLs) |
| nui | VARCHAR(50) | | Business registration number |
| tvsh | VARCHAR(50) | | VAT number |
| email | VARCHAR(200) | | |
| phone | VARCHAR(50) | | |
| address | VARCHAR(300) | | |
| city | VARCHAR(100) | | "Ferizaj" |
| representative | VARCHAR(200) | | Legal representative name |
| bank_name | VARCHAR(100) | | "TEB" |
| bank_account | VARCHAR(50) | | "2013000010578275" |
| license_number | VARCHAR(50) | | "R-561-05-B/25" |
| logo_url | VARCHAR(500) | | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

#### users
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| username | VARCHAR(100) | NOT NULL | Unique per tenant |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed |
| full_name | VARCHAR(200) | NOT NULL | |
| personal_number | VARCHAR(20) | | Kosovo personal ID |
| email | VARCHAR(200) | | |
| role | VARCHAR(50) | NOT NULL | 'super_admin', 'administrator', 'instructor', 'lecturer' |
| is_active | BOOLEAN | DEFAULT TRUE | |
| activation_count | INTEGER | DEFAULT 0 | |
| last_login_at | TIMESTAMP | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| end_date | TIMESTAMP | | Account expiry |

**Index**: `idx_users_tenant_id` on `tenant_id`
**Unique**: `(tenant_id, username)` — usernames unique within tenant

#### sessions
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| user_id | UUID | FK → users.id, NOT NULL | |
| access_token | TEXT | NOT NULL | JWT access token |
| refresh_token | TEXT | NOT NULL | JWT refresh token |
| impersonated_by | UUID | FK → users.id, NULLABLE | Super-admin who is impersonating |
| expires_at | TIMESTAMP | NOT NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 3. Driving School Configuration

#### categories
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| code | VARCHAR(10) | NOT NULL | B, BD, C, CE, D |
| description | VARCHAR(300) | | |
| verification_text | TEXT | | Text shown on vërtetim document |
| verification_code | VARCHAR(50) | | |
| theory_hours | INTEGER | DEFAULT 20 | |
| practical_hours | INTEGER | DEFAULT 20 | |
| price | DECIMAL(10,2) | DEFAULT 350.00 | |
| contract_price | DECIMAL(10,2) | | |
| is_licensed | BOOLEAN | DEFAULT FALSE | School licensed for this category |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Unique**: `(tenant_id, code)`

#### licenses
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| category_id | UUID | FK → categories.id, NOT NULL | |
| license_code | VARCHAR(50) | NOT NULL | "R-561-05-B/25" |
| issue_date | DATE | | |
| expiry_date | DATE | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 4. Staff

#### instructors
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| user_id | UUID | FK → users.id, NULLABLE, UNIQUE | Linked user account for login |
| code | VARCHAR(20) | NOT NULL | Legacy code "1000000001" |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| personal_number | VARCHAR(20) | | Kosovo personal ID |
| email | VARCHAR(200) | | Login email (synced with users.email) |
| phone | VARCHAR(50) | | |
| position | VARCHAR(20) | NOT NULL | 'instructor', 'lecturer', 'both' |
| hours_realized | INTEGER | DEFAULT 0 | Total hours tracked |
| license_info | VARCHAR(200) | | License details |
| cost_per_candidate | DECIMAL(10,2) | DEFAULT 65.00 | Amount instructor pays per candidate (€) |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Unique**: `(tenant_id, code)`
**Index**: `idx_instructors_tenant_id` on `tenant_id`
**Index**: `idx_instructors_user_id` on `user_id`

**Instructor Login Flow**: When an instructor is created with an email and password, a corresponding `users` record is created with `role='instructor'`. The `user_id` FK links instructor → user for login. Instructors can only view candidates assigned to them (read-only, no candidate creation).

---

### 5. Vehicles

#### vehicles
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| make | VARCHAR(100) | NOT NULL | e.g., "Volkswagen Golf" |
| model | VARCHAR(100) | | |
| chassis_number | VARCHAR(50) | | |
| plate_number | VARCHAR(20) | NOT NULL | |
| registration_date | DATE | | |
| registration_expiry | DATE | | |
| technical_control_date | DATE | | |
| instructor_id | UUID | FK → instructors.id, NULLABLE | Assigned instructor |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_vehicles_tenant_id` on `tenant_id`

---

### 6. Candidates (Core Entity)

#### candidates
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| code | VARCHAR(20) | NOT NULL | Legacy "1000005274" |
| first_name | VARCHAR(100) | NOT NULL | Emri |
| parent_name | VARCHAR(100) | | Emri i Prindit |
| last_name | VARCHAR(100) | NOT NULL | Mbiemri |
| personal_number | VARCHAR(20) | NOT NULL | Numri Personal (10 digits) |
| phone | VARCHAR(50) | | |
| email | VARCHAR(200) | | |
| birth_country_id | UUID | FK → countries.id | |
| birth_municipality_id | UUID | FK → municipalities.id | |
| birth_place_id | UUID | FK → places.id | |
| birth_municipality_foreign | VARCHAR(200) | | For non-Kosovo births |
| birth_place_foreign | VARCHAR(200) | | For non-Kosovo births |
| date_of_birth | DATE | | |
| gender | VARCHAR(1) | CHECK IN ('M', 'F') | |
| residence_municipality_id | UUID | FK → municipalities.id | |
| residence_place_id | UUID | FK → places.id | |
| category_id | UUID | FK → categories.id, NOT NULL | |
| is_automatic | BOOLEAN | DEFAULT FALSE | Automatic transmission |
| price | DECIMAL(10,2) | NOT NULL | Total price |
| amount_paid | DECIMAL(10,2) | DEFAULT 0.00 | Running total |
| practical_hours | INTEGER | DEFAULT 20 | Allocated hours |
| theory_hours | INTEGER | DEFAULT 20 | Allocated hours |
| practical_hours_realized | INTEGER | DEFAULT 0 | Completed hours |
| registration_date | DATE | NOT NULL | |
| protocol_number | VARCHAR(50) | | Numri Rendor |
| medical_certificate | BOOLEAN | DEFAULT FALSE | |
| medical_certificate_number | VARCHAR(50) | | |
| medical_certificate_date | DATE | | |
| verification_flag | BOOLEAN | DEFAULT FALSE | Vërtetimi A.Sh. |
| red_cross_certificate | BOOLEAN | DEFAULT FALSE | |
| id_card_copy | BOOLEAN | DEFAULT FALSE | Leternjoftimi |
| lecturer_id | UUID | FK → instructors.id, NULLABLE | |
| instructor_id | UUID | FK → instructors.id, NULLABLE | |
| vehicle_id | UUID | FK → vehicles.id, NULLABLE | |
| has_extra_hours | BOOLEAN | DEFAULT FALSE | Ore Shtese flag |
| is_archived | BOOLEAN | DEFAULT FALSE | Moved to Arkiva |
| comments | TEXT | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |
| deleted_at | TIMESTAMP | NULLABLE | Soft delete |

**Indexes**:
- `idx_candidates_tenant_id` on `tenant_id`
- `idx_candidates_personal_number` on `(tenant_id, personal_number)`
- `idx_candidates_category` on `(tenant_id, category_id)`
- `idx_candidates_registration_date` on `(tenant_id, registration_date)`
- `idx_candidates_is_archived` on `(tenant_id, is_archived)`
- `idx_candidates_instructor` on `(tenant_id, instructor_id)`

**Unique**: `(tenant_id, code)`

---

### 7. Theory Hours

#### theory_hour_sessions
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| session_number | INTEGER | NOT NULL | 1-8 for category B |
| chapter_topics | VARCHAR(100) | NOT NULL | "1.1, 1.2, 1.3" |
| date_realized | DATE | | |
| time_from | TIME | DEFAULT '16:00' | |
| time_to | TIME | DEFAULT '17:30' | |
| hours_count | INTEGER | DEFAULT 2 | |
| is_realized | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Unique**: `(candidate_id, session_number)`

---

### 8. Practical Hours

#### practical_hour_sessions
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| instructor_id | UUID | FK → instructors.id, NULLABLE | |
| date_realized | DATE | NOT NULL | |
| time_realized | TIME | NOT NULL | |
| hours_count | INTEGER | DEFAULT 1 | |
| price_per_hour | DECIMAL(10,2) | DEFAULT 0.00 | |
| remarks | TEXT | | Verejtje |
| is_paid | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_practical_hours_candidate` on `(tenant_id, candidate_id)`
**Index**: `idx_practical_hours_instructor` on `(tenant_id, instructor_id)`

---

### 9. Supplementary Hours

#### supplementary_registrations
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| category_id | UUID | FK → categories.id, NOT NULL | |
| is_automatic | BOOLEAN | DEFAULT FALSE | |
| price | DECIMAL(10,2) | | |
| practical_hours | INTEGER | | |
| theory_hours | INTEGER | | |
| registration_date | DATE | NOT NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 10. Verifications

#### verifications
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| category_id | UUID | FK → categories.id, NOT NULL | |
| verification_date | DATE | | |
| theory_hours_start | DATE | | Ore Teorike Fillimi |
| theory_hours_end | DATE | | Ore Teorike Mbarimi |
| practical_hours_start | DATE | | Ore Praktike Fillimi |
| practical_hours_end | DATE | | Ore Praktike Mbarimi |
| sequence_number | VARCHAR(50) | | Numri rendore |
| lecturer_id | UUID | FK → instructors.id, NULLABLE | |
| instructor_id | UUID | FK → instructors.id, NULLABLE | |
| red_cross_cert | BOOLEAN | DEFAULT FALSE | |
| id_card_copy | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 11. Payments

#### payments
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| amount | DECIMAL(10,2) | NOT NULL | |
| payment_method | VARCHAR(50) | | Cash, bank transfer, etc. |
| payment_date | DATE | NOT NULL | |
| received_by_user_id | UUID | FK → users.id, NULLABLE | Kryer nga |
| is_supplementary | BOOLEAN | DEFAULT FALSE | For extra hours |
| remarks | TEXT | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_payments_candidate` on `(tenant_id, candidate_id)`
**Index**: `idx_payments_date` on `(tenant_id, payment_date)`

---

### 12. Expenses

#### expense_types
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| name | VARCHAR(200) | NOT NULL | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

#### expenses
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| vehicle_id | UUID | FK → vehicles.id, NULLABLE | |
| expense_type_id | UUID | FK → expense_types.id, NOT NULL | |
| date | DATE | NOT NULL | |
| amount | DECIMAL(10,2) | NOT NULL | |
| description | TEXT | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 13. Tests (Basic - not the paid module)

#### candidate_tests
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| test_number | INTEGER | | Test provues number |
| score | INTEGER | | Points achieved |
| passing_score | INTEGER | DEFAULT 85 | Pikët e arritura |
| date_taken | DATE | | |
| is_passed | BOOLEAN | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 14. Audit Log

#### audit_logs
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | NULLABLE | NULL for super-admin actions |
| user_id | UUID | FK → users.id | |
| action | VARCHAR(50) | NOT NULL | 'create', 'update', 'delete', 'login', 'impersonate' |
| entity_type | VARCHAR(100) | | 'candidate', 'payment', etc. |
| entity_id | UUID | | |
| old_values | JSONB | | Previous state |
| new_values | JSONB | | New state |
| ip_address | VARCHAR(50) | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_audit_logs_tenant_date` on `(tenant_id, created_at)`

---

### 15. Instructor Payments (Debt Tracking)

#### instructor_payments
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| instructor_id | UUID | FK → instructors.id, NOT NULL | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | Candidate this charge is for |
| amount | DECIMAL(10,2) | NOT NULL | Amount owed (default 65.00€) |
| amount_paid | DECIMAL(10,2) | DEFAULT 0.00 | Amount paid so far |
| payment_date | DATE | NULLABLE | Date of payment (NULL if unpaid) |
| payment_method | VARCHAR(50) | | Cash, bank transfer, etc. |
| status | VARCHAR(20) | DEFAULT 'unpaid' | 'unpaid', 'partial', 'paid' |
| remarks | TEXT | | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Note**: A record is auto-created when a candidate is assigned to an instructor. The `amount` defaults to `instructors.cost_per_candidate` (65€).

**Index**: `idx_instructor_payments_tenant` on `(tenant_id, instructor_id)`
**Index**: `idx_instructor_payments_status` on `(tenant_id, status)`
**Unique**: `(tenant_id, instructor_id, candidate_id)` — one charge per instructor-candidate pair

---

### 16. Messages (Instructor ↔ Admin Communication)

#### messages
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| conversation_id | UUID | NOT NULL | Groups messages into threads |
| sender_id | UUID | FK → users.id, NOT NULL | |
| recipient_id | UUID | FK → users.id, NULLABLE | NULL = broadcast to all admins |
| content | TEXT | NOT NULL | Message text |
| is_read | BOOLEAN | DEFAULT FALSE | |
| read_at | TIMESTAMP | NULLABLE | |
| created_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_messages_conversation` on `(tenant_id, conversation_id, created_at)`
**Index**: `idx_messages_recipient` on `(tenant_id, recipient_id, is_read)`

#### conversations
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| subject | VARCHAR(300) | NOT NULL | Conversation subject |
| participant_ids | UUID[] | NOT NULL | Array of user_ids in conversation |
| last_message_at | TIMESTAMP | | For sorting conversations |
| created_by | UUID | FK → users.id, NOT NULL | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Index**: `idx_conversations_tenant` on `(tenant_id, last_message_at DESC)`

---

### 17. Calendar / Practical Lesson Scheduling

#### scheduled_lessons
| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → tenants.id, NOT NULL | |
| instructor_id | UUID | FK → instructors.id, NOT NULL | |
| candidate_id | UUID | FK → candidates.id, NOT NULL | |
| vehicle_id | UUID | FK → vehicles.id, NULLABLE | |
| scheduled_date | DATE | NOT NULL | |
| start_time | TIME | NOT NULL | |
| end_time | TIME | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'scheduled' | 'scheduled', 'completed', 'cancelled', 'no_show' |
| notes | TEXT | | |
| cancelled_reason | TEXT | | If status = 'cancelled' |
| practical_session_id | UUID | FK → practical_hour_sessions.id, NULLABLE | Linked after completion |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Note**: When a scheduled lesson is marked 'completed', a corresponding `practical_hour_sessions` record is created and linked via `practical_session_id`.

**Index**: `idx_scheduled_lessons_instructor_date` on `(tenant_id, instructor_id, scheduled_date)`
**Index**: `idx_scheduled_lessons_candidate_date` on `(tenant_id, candidate_id, scheduled_date)`
**Index**: `idx_scheduled_lessons_date` on `(tenant_id, scheduled_date, start_time)`

---

## Migration Notes
- Use Alembic (via Flask-Migrate) for all schema changes
- Never modify migrations after they've been applied
- Seed data: `flask seed-locations` populates countries, municipalities, places
- Seed data: `flask seed-categories` populates default category configs
