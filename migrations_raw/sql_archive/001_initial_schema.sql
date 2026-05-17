-- AutoShkolla Pro - Initial Database Schema Migration
-- Run: psql -d autoshkolla_pro -f migrations/001_initial_schema.sql
-- Date: 2026-03-09

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. SHARED REFERENCE DATA (No tenant_id)
-- ============================================================

CREATE TABLE countries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE municipalities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    country_id UUID NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(country_id, name)
);

CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    municipality_id UUID NOT NULL REFERENCES municipalities(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    zip_code VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(municipality_id, name)
);

CREATE INDEX idx_municipalities_country ON municipalities(country_id);
CREATE INDEX idx_places_municipality ON places(municipality_id);

-- ============================================================
-- 2. TENANTS
-- ============================================================

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    contact_email VARCHAR(200),
    contact_phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(200) NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'administrator',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);

-- ============================================================
-- 4. CATEGORIES
-- ============================================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100),
    theory_hours INTEGER DEFAULT 20,
    practical_hours INTEGER DEFAULT 20,
    price DECIMAL(10,2) DEFAULT 350.00,
    verification_text TEXT,
    verification_code VARCHAR(50),
    contract_price DECIMAL(10,2),
    is_licensed BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_categories_tenant ON categories(tenant_id);

-- ============================================================
-- 5. INSTRUCTORS
-- ============================================================

CREATE TABLE instructors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE SET NULL,
    code VARCHAR(20) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    personal_number VARCHAR(20),
    email VARCHAR(200),
    phone VARCHAR(50),
    position VARCHAR(20) NOT NULL DEFAULT 'instructor',
    hours_realized INTEGER DEFAULT 0,
    license_info VARCHAR(200),
    cost_per_candidate DECIMAL(10,2) DEFAULT 65.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_instructors_tenant ON instructors(tenant_id);
CREATE INDEX idx_instructors_user ON instructors(user_id);

-- ============================================================
-- 6. VEHICLES
-- ============================================================

CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    chassis_number VARCHAR(50),
    plate_number VARCHAR(20) NOT NULL,
    registration_date DATE,
    registration_expiry DATE,
    technical_control_date DATE,
    instructor_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vehicles_tenant ON vehicles(tenant_id);
CREATE INDEX idx_vehicles_instructor ON vehicles(tenant_id, instructor_id);

-- ============================================================
-- 7. CANDIDATES (Core Entity)
-- ============================================================

CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    parent_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    personal_number VARCHAR(20) NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(200),
    birth_country_id UUID REFERENCES countries(id),
    birth_municipality_id UUID REFERENCES municipalities(id),
    birth_place_id UUID REFERENCES places(id),
    birth_municipality_foreign VARCHAR(200),
    birth_place_foreign VARCHAR(200),
    date_of_birth DATE,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F')),
    residence_municipality_id UUID REFERENCES municipalities(id),
    residence_place_id UUID REFERENCES places(id),
    category_id UUID NOT NULL REFERENCES categories(id),
    is_automatic BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0.00,
    practical_hours INTEGER DEFAULT 20,
    theory_hours INTEGER DEFAULT 20,
    practical_hours_realized INTEGER DEFAULT 0,
    registration_date DATE NOT NULL,
    protocol_number VARCHAR(50),
    medical_certificate BOOLEAN DEFAULT FALSE,
    medical_certificate_number VARCHAR(50),
    medical_certificate_date DATE,
    verification_flag BOOLEAN DEFAULT FALSE,
    red_cross_certificate BOOLEAN DEFAULT FALSE,
    id_card_copy BOOLEAN DEFAULT FALSE,
    lecturer_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    instructor_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    has_extra_hours BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    comments TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_candidates_tenant ON candidates(tenant_id);
CREATE INDEX idx_candidates_personal_number ON candidates(tenant_id, personal_number);
CREATE INDEX idx_candidates_category ON candidates(tenant_id, category_id);
CREATE INDEX idx_candidates_registration_date ON candidates(tenant_id, registration_date);
CREATE INDEX idx_candidates_archived ON candidates(tenant_id, is_archived);
CREATE INDEX idx_candidates_instructor ON candidates(tenant_id, instructor_id);

-- ============================================================
-- 8. THEORY HOUR SESSIONS
-- ============================================================

CREATE TABLE theory_hour_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    session_number INTEGER NOT NULL,
    chapter_topics VARCHAR(100) NOT NULL,
    date_realized DATE,
    time_from TIME DEFAULT '16:00',
    time_to TIME DEFAULT '17:30',
    hours_count INTEGER DEFAULT 2,
    is_realized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(candidate_id, session_number)
);

CREATE INDEX idx_theory_sessions_candidate ON theory_hour_sessions(tenant_id, candidate_id);

-- ============================================================
-- 9. PRACTICAL HOUR SESSIONS
-- ============================================================

CREATE TABLE practical_hour_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    instructor_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    date_realized DATE NOT NULL,
    time_realized TIME NOT NULL,
    hours_count INTEGER DEFAULT 1,
    price_per_hour DECIMAL(10,2) DEFAULT 0.00,
    remarks TEXT,
    is_paid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_practical_sessions_candidate ON practical_hour_sessions(tenant_id, candidate_id);
CREATE INDEX idx_practical_sessions_instructor ON practical_hour_sessions(tenant_id, instructor_id);
CREATE INDEX idx_practical_sessions_date ON practical_hour_sessions(tenant_id, date_realized);

-- ============================================================
-- 10. SUPPLEMENTARY REGISTRATIONS
-- ============================================================

CREATE TABLE supplementary_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id),
    is_automatic BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2),
    practical_hours INTEGER,
    theory_hours INTEGER,
    registration_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_supplementary_candidate ON supplementary_registrations(tenant_id, candidate_id);

-- ============================================================
-- 11. VERIFICATIONS
-- ============================================================

CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id),
    verification_date DATE,
    theory_hours_start DATE,
    theory_hours_end DATE,
    practical_hours_start DATE,
    practical_hours_end DATE,
    sequence_number VARCHAR(50),
    lecturer_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    instructor_id UUID REFERENCES instructors(id) ON DELETE SET NULL,
    red_cross_cert BOOLEAN DEFAULT FALSE,
    id_card_copy BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verifications_candidate ON verifications(tenant_id, candidate_id);

-- ============================================================
-- 12. PAYMENTS
-- ============================================================

CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_date DATE NOT NULL,
    received_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    is_supplementary BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_candidate ON payments(tenant_id, candidate_id);
CREATE INDEX idx_payments_date ON payments(tenant_id, payment_date);

-- ============================================================
-- 13. CANDIDATE TESTS
-- ============================================================

CREATE TABLE candidate_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    test_number INTEGER,
    score INTEGER,
    passing_score INTEGER DEFAULT 85,
    date_taken DATE,
    is_passed BOOLEAN,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_candidate_tests_candidate ON candidate_tests(tenant_id, candidate_id);

-- ============================================================
-- 14. EXPENSE TYPES
-- ============================================================

CREATE TABLE expense_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_expense_types_tenant ON expense_types(tenant_id);

-- ============================================================
-- 15. EXPENSES
-- ============================================================

CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    expense_type_id UUID NOT NULL REFERENCES expense_types(id),
    date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expenses_tenant_date ON expenses(tenant_id, date);
CREATE INDEX idx_expenses_vehicle ON expenses(tenant_id, vehicle_id);
CREATE INDEX idx_expenses_type ON expenses(tenant_id, expense_type_id);

-- ============================================================
-- 16. INSTRUCTOR PAYMENTS (Debt Tracking)
-- ============================================================

CREATE TABLE instructor_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    instructor_id UUID NOT NULL REFERENCES instructors(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL DEFAULT 65.00,
    amount_paid DECIMAL(10,2) DEFAULT 0.00,
    payment_date DATE,
    payment_method VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'unpaid',
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, instructor_id, candidate_id)
);

CREATE INDEX idx_instructor_payments_tenant ON instructor_payments(tenant_id, instructor_id);
CREATE INDEX idx_instructor_payments_status ON instructor_payments(tenant_id, status);

-- ============================================================
-- 17. SCHEDULED LESSONS (Calendar)
-- ============================================================

CREATE TABLE scheduled_lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    instructor_id UUID NOT NULL REFERENCES instructors(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE SET NULL,
    scheduled_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    notes TEXT,
    cancelled_reason TEXT,
    practical_session_id UUID REFERENCES practical_hour_sessions(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scheduled_lessons_instructor_date ON scheduled_lessons(tenant_id, instructor_id, scheduled_date);
CREATE INDEX idx_scheduled_lessons_candidate_date ON scheduled_lessons(tenant_id, candidate_id, scheduled_date);
CREATE INDEX idx_scheduled_lessons_date ON scheduled_lessons(tenant_id, scheduled_date, start_time);

-- ============================================================
-- 18. CONVERSATIONS
-- ============================================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    subject VARCHAR(200) NOT NULL,
    participant_ids UUID[] NOT NULL DEFAULT '{}',
    last_message_at TIMESTAMP,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX idx_conversations_created_by ON conversations(tenant_id, created_by);

-- ============================================================
-- 19. MESSAGES
-- ============================================================

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES users(id),
    recipient_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_sender ON messages(tenant_id, sender_id);
CREATE INDEX idx_messages_recipient ON messages(tenant_id, recipient_id, is_read);

-- ============================================================
-- 20. AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant_date ON audit_logs(tenant_id, created_at);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
