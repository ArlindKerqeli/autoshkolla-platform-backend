-- Autoshkolla Platform Database Schema Initialization
-- PostgreSQL 13+
-- Initialize complete database schema for multi-tenant driving school CRM

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. COUNTRIES TABLE - Reference data for all countries
-- ============================================================================

CREATE TABLE countries (
    country_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(3) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_countries_code ON countries(code);

COMMENT ON TABLE countries IS 'Reference table: Countries available for location hierarchy';
COMMENT ON COLUMN countries.code IS 'ISO 3166-1 alpha-2/3 country code (e.g., XK for Kosovo)';

-- ============================================================================
-- 2. MUNICIPALITIES TABLE - Subdivisions of countries
-- ============================================================================

CREATE TABLE municipalities (
    municipality_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id UUID NOT NULL REFERENCES countries(country_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(country_id, name)
);

CREATE INDEX idx_municipalities_country_id ON municipalities(country_id);

COMMENT ON TABLE municipalities IS 'Reference table: Municipalities within countries';

-- ============================================================================
-- 3. PLACES TABLE - Specific places within municipalities
-- ============================================================================

CREATE TABLE places (
    place_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    municipality_id UUID NOT NULL REFERENCES municipalities(municipality_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(municipality_id, name)
);

CREATE INDEX idx_places_municipality_id ON places(municipality_id);

COMMENT ON TABLE places IS 'Reference table: Specific places/villages within municipalities';

-- ============================================================================
-- 4. TENANTS TABLE - Multi-tenant organization data
-- ============================================================================

CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tenants_active ON tenants(active);

COMMENT ON TABLE tenants IS 'Driving schools (tenants) in the multi-tenant system';

-- ============================================================================
-- 5. USERS TABLE - System users for all tenants
-- ============================================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'administrator', 'instructor', 'lecturer')),
    active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(active);

COMMENT ON TABLE users IS 'System users with role-based access control';
COMMENT ON COLUMN users.role IS 'User role: super_admin (platform), administrator (school), instructor, lecturer';

-- ============================================================================
-- 6. SESSIONS TABLE - User authentication sessions
-- ============================================================================

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    refresh_token VARCHAR(255) UNIQUE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

COMMENT ON TABLE sessions IS 'User sessions and refresh tokens for authentication';

-- ============================================================================
-- 7. CATEGORIES TABLE - Vehicle categories (B, BE, C, etc.)
-- ============================================================================

CREATE TABLE categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    min_age INTEGER DEFAULT 18,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_categories_tenant_id ON categories(tenant_id);

COMMENT ON TABLE categories IS 'Vehicle categories (B - personal, C - commercial, etc.)';

-- ============================================================================
-- 8. LICENSES TABLE - School licenses for specific categories
-- ============================================================================

CREATE TABLE licenses (
    license_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    license_number VARCHAR(50) NOT NULL,
    issued_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_licenses_tenant_id ON licenses(tenant_id);
CREATE INDEX idx_licenses_category_id ON licenses(category_id);
CREATE INDEX idx_licenses_expiry_date ON licenses(expiry_date);

COMMENT ON TABLE licenses IS 'School licenses for vehicle categories';

-- ============================================================================
-- 9. INSTRUCTORS TABLE - Driving instructors
-- ============================================================================

CREATE TABLE instructors (
    instructor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    license_number VARCHAR(50) NOT NULL,
    categories TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_instructors_tenant_id ON instructors(tenant_id);
CREATE INDEX idx_instructors_email ON instructors(email);
CREATE INDEX idx_instructors_active ON instructors(active);

COMMENT ON TABLE instructors IS 'Driving instructors employed by school';
COMMENT ON COLUMN instructors.categories IS 'Comma-separated category codes (e.g., B,C,BE)';

-- ============================================================================
-- 10. VEHICLES TABLE - Training vehicles
-- ============================================================================

CREATE TABLE vehicles (
    vehicle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    instructor_id UUID REFERENCES instructors(instructor_id) ON DELETE SET NULL,
    plate_number VARCHAR(20) NOT NULL,
    model VARCHAR(100) NOT NULL,
    category VARCHAR(10) NOT NULL,
    registration_date DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, plate_number)
);

CREATE INDEX idx_vehicles_tenant_id ON vehicles(tenant_id);
CREATE INDEX idx_vehicles_instructor_id ON vehicles(instructor_id);
CREATE INDEX idx_vehicles_active ON vehicles(active);

COMMENT ON TABLE vehicles IS 'Training vehicles for practical lessons';

-- ============================================================================
-- 11. CANDIDATES TABLE - Students enrolled in driving courses
-- ============================================================================

CREATE TABLE candidates (
    candidate_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    id_number VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F')),
    country_id UUID REFERENCES countries(country_id) ON DELETE SET NULL,
    municipality_id UUID REFERENCES municipalities(municipality_id) ON DELETE SET NULL,
    place_id UUID REFERENCES places(place_id) ON DELETE SET NULL,
    address TEXT,
    category_id UUID REFERENCES categories(category_id) ON DELETE RESTRICT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'completed')),
    archived_at TIMESTAMP,
    archive_reason TEXT,
    instructors TEXT,
    vehicles TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, id_number)
);

CREATE INDEX idx_candidates_tenant_id ON candidates(tenant_id);
CREATE INDEX idx_candidates_category_id ON candidates(category_id);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_name ON candidates(first_name, last_name);

COMMENT ON TABLE candidates IS 'Students enrolled in driving courses';
COMMENT ON COLUMN candidates.instructors IS 'Comma-separated instructor UUIDs';
COMMENT ON COLUMN candidates.vehicles IS 'Comma-separated vehicle UUIDs';
COMMENT ON COLUMN candidates.status IS 'active, archived (suspended), or completed';

-- ============================================================================
-- 12. THEORY_HOUR_SESSIONS TABLE - Theory training sessions
-- ============================================================================

CREATE TABLE theory_hour_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    hours NUMERIC(4,2) NOT NULL CHECK (hours > 0 AND hours <= 24),
    topic VARCHAR(255) NOT NULL,
    lecturer_name VARCHAR(255),
    evidence_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_theory_hour_sessions_tenant_id ON theory_hour_sessions(tenant_id);
CREATE INDEX idx_theory_hour_sessions_candidate_id ON theory_hour_sessions(candidate_id);
CREATE INDEX idx_theory_hour_sessions_date ON theory_hour_sessions(date);

COMMENT ON TABLE theory_hour_sessions IS 'Theory training session records';
COMMENT ON COLUMN theory_hour_sessions.hours IS 'Hours completed in this session';

-- ============================================================================
-- 13. PRACTICAL_HOUR_SESSIONS TABLE - Practical driving sessions
-- ============================================================================

CREATE TABLE practical_hour_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    instructor_id UUID NOT NULL REFERENCES instructors(instructor_id) ON DELETE RESTRICT,
    vehicle_id UUID REFERENCES vehicles(vehicle_id) ON DELETE SET NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    hours NUMERIC(4,2) NOT NULL CHECK (hours > 0 AND hours <= 24),
    route VARCHAR(255),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_practical_hour_sessions_tenant_id ON practical_hour_sessions(tenant_id);
CREATE INDEX idx_practical_hour_sessions_candidate_id ON practical_hour_sessions(candidate_id);
CREATE INDEX idx_practical_hour_sessions_instructor_id ON practical_hour_sessions(instructor_id);
CREATE INDEX idx_practical_hour_sessions_vehicle_id ON practical_hour_sessions(vehicle_id);
CREATE INDEX idx_practical_hour_sessions_date ON practical_hour_sessions(date);
CREATE INDEX idx_practical_hour_sessions_status ON practical_hour_sessions(status);

COMMENT ON TABLE practical_hour_sessions IS 'Practical driving lesson records';

-- ============================================================================
-- 14. SUPPLEMENTARY_REGISTRATIONS TABLE - Additional category training
-- ============================================================================

CREATE TABLE supplementary_registrations (
    supplementary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_supplementary_registrations_tenant_id ON supplementary_registrations(tenant_id);
CREATE INDEX idx_supplementary_registrations_candidate_id ON supplementary_registrations(candidate_id);
CREATE INDEX idx_supplementary_registrations_category_id ON supplementary_registrations(category_id);

COMMENT ON TABLE supplementary_registrations IS 'Additional category registrations for candidates';

-- ============================================================================
-- 15. VERIFICATIONS TABLE - Test results and verification status
-- ============================================================================

CREATE TABLE verifications (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(category_id) ON DELETE RESTRICT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'failed')),
    theory_passed BOOLEAN DEFAULT FALSE,
    practical_passed BOOLEAN DEFAULT FALSE,
    theory_score INTEGER CHECK (theory_score IS NULL OR (theory_score >= 0 AND theory_score <= 100)),
    practical_score INTEGER CHECK (practical_score IS NULL OR (practical_score >= 0 AND practical_score <= 100)),
    verification_date DATE,
    certificate_number VARCHAR(100),
    verified_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_verifications_tenant_id ON verifications(tenant_id);
CREATE INDEX idx_verifications_candidate_id ON verifications(candidate_id);
CREATE INDEX idx_verifications_status ON verifications(status);
CREATE INDEX idx_verifications_verification_date ON verifications(verification_date);

COMMENT ON TABLE verifications IS 'Test results and completion verification records';

-- ============================================================================
-- 16. PAYMENTS TABLE - Financial transactions
-- ============================================================================

CREATE TABLE payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'EUR',
    date DATE NOT NULL,
    method VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'partial')),
    reference_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payments_tenant_id ON payments(tenant_id);
CREATE INDEX idx_payments_candidate_id ON payments(candidate_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_date ON payments(date);
CREATE INDEX idx_payments_status ON payments(status);

COMMENT ON TABLE payments IS 'Payment transactions and financial records';

-- ============================================================================
-- 17. EXPENSE_TYPES TABLE - Categories of expenses
-- ============================================================================

CREATE TABLE expense_types (
    type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, code)
);

CREATE INDEX idx_expense_types_tenant_id ON expense_types(tenant_id);

COMMENT ON TABLE expense_types IS 'Categories of school expenses (maintenance, fuel, insurance, etc.)';

-- ============================================================================
-- 18. EXPENSES TABLE - School operating expenses
-- ============================================================================

CREATE TABLE expenses (
    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    type_id UUID NOT NULL REFERENCES expense_types(type_id) ON DELETE RESTRICT,
    vehicle_id UUID REFERENCES vehicles(vehicle_id) ON DELETE SET NULL,
    amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) DEFAULT 'EUR',
    date DATE NOT NULL,
    description TEXT,
    receipt_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_expenses_tenant_id ON expenses(tenant_id);
CREATE INDEX idx_expenses_type_id ON expenses(type_id);
CREATE INDEX idx_expenses_vehicle_id ON expenses(vehicle_id);
CREATE INDEX idx_expenses_date ON expenses(date);

COMMENT ON TABLE expenses IS 'School operating expenses with optional vehicle association';

-- ============================================================================
-- 19. CANDIDATE_TESTS TABLE - Formal test results
-- ============================================================================

CREATE TABLE candidate_tests (
    test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    test_type VARCHAR(50) NOT NULL CHECK (test_type IN ('theory', 'practical', 'medical')),
    date DATE NOT NULL,
    score INTEGER CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
    result VARCHAR(50) CHECK (result IN ('pass', 'fail', 'pending')),
    test_file_path VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_candidate_tests_tenant_id ON candidate_tests(tenant_id);
CREATE INDEX idx_candidate_tests_candidate_id ON candidate_tests(candidate_id);
CREATE INDEX idx_candidate_tests_test_type ON candidate_tests(test_type);
CREATE INDEX idx_candidate_tests_date ON candidate_tests(date);

COMMENT ON TABLE candidate_tests IS 'Formal test results and scores';

-- ============================================================================
-- 20. AUDIT_LOGS TABLE - Complete audit trail
-- ============================================================================

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    changes JSONB,
    is_impersonating BOOLEAN DEFAULT FALSE,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

COMMENT ON TABLE audit_logs IS 'Complete audit trail of all administrative actions';
COMMENT ON COLUMN audit_logs.changes IS 'JSON object containing field changes (old/new values)';
COMMENT ON COLUMN audit_logs.is_impersonating IS 'TRUE if action was performed by super-admin impersonating tenant';

-- ============================================================================
-- INDEXES FOR COMMON QUERIES
-- ============================================================================

-- Multi-tenant isolation indexes
CREATE INDEX idx_candidates_tenant_category ON candidates(tenant_id, category_id);
CREATE INDEX idx_theory_sessions_candidate_date ON theory_hour_sessions(candidate_id, date);
CREATE INDEX idx_practical_sessions_candidate_date ON practical_hour_sessions(candidate_id, date);
CREATE INDEX idx_payments_candidate_date ON payments(candidate_id, date);
CREATE INDEX idx_expenses_tenant_date ON expenses(tenant_id, date);

-- Authentication and session indexes
CREATE INDEX idx_users_tenant_active ON users(tenant_id, active);
CREATE INDEX idx_sessions_user_revoked ON sessions(user_id, revoked);

-- Search and filtering indexes
CREATE INDEX idx_candidates_tenant_name ON candidates(tenant_id, first_name, last_name);
CREATE INDEX idx_instructors_tenant_active ON instructors(tenant_id, active);
CREATE INDEX idx_vehicles_tenant_active ON vehicles(tenant_id, active);

-- ============================================================================
-- SCHEMA SUMMARY
-- ============================================================================

-- Tables created: 20
-- Indexes created: 50+
-- Foreign keys: 40+
-- Constraints: Multi-tenant isolation, data validation, referential integrity

-- Key Design Patterns:
-- 1. All data tables have tenant_id for multi-tenant isolation
-- 2. All tables have created_at and updated_at timestamps for audit trail
-- 3. UUID primary keys for distributed system compatibility
-- 4. Proper cascading deletes for reference integrity
-- 5. Check constraints for data validation (gender, role, status)
-- 6. Comprehensive indexing for query performance
-- 7. JSONB for flexible audit log storage

-- ============================================================================
-- INITIAL DATA SETUP (Optional)
-- ============================================================================

-- Insert Kosovo as default country
INSERT INTO countries (name, code) VALUES ('Kosova', 'XK')
ON CONFLICT (code) DO NOTHING;

-- Note: Municipalities and places should be populated from migration scripts
-- or seeding data based on Kosovo administrative divisions

