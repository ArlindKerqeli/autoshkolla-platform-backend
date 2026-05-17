import pytest
import uuid
import os
from datetime import date, datetime

# SAFETY: Force DATABASE_URL to test database BEFORE any app imports.
# This prevents accidentally connecting to (and wiping) the dev database.
_TEST_DB_URL = os.getenv(
    'TEST_DATABASE_URL',
    'postgresql://autoshkolla:dev_password@localhost:5432/autoshkolla_pro_test',
)
os.environ['DATABASE_URL'] = _TEST_DB_URL
os.environ['FLASK_ENV'] = 'testing'
os.environ['JWT_SECRET'] = 'test-jwt-secret'
os.environ['SECRET_KEY'] = 'test-secret-key'

from app import create_app
from app.utils.db import db as _db
from app.models.tenant_model import Tenant
from app.models.user_model import User
from app.models.category_model import Category
from app.models.instructor_model import Instructor
from app.models.vehicle_model import Vehicle
from app.models.candidate_model import Candidate
from app.models.instructor_payment_model import InstructorPayment
from app.utils.jwt import encode_access_token


# ---------------------------------------------------------------------------
# App + DB fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope='session')
def app():
    """Create Flask application for testing."""
    # Double-check we're on the test database
    db_url = os.environ.get('DATABASE_URL', '')
    assert 'test' in db_url, f'SAFETY: Refusing to run tests against non-test database: {db_url}'

    app = create_app()

    with app.app_context():
        _db.create_all()

    yield app

    with app.app_context():
        _db.session.remove()
        _db.session.execute(_db.text('DROP SCHEMA public CASCADE'))
        _db.session.execute(_db.text('CREATE SCHEMA public'))
        _db.session.commit()


@pytest.fixture(autouse=True)
def _app_context(app):
    """Push app context for every test and clean up DB after."""
    ctx = app.app_context()
    ctx.push()
    yield
    _db.session.rollback()
    # Truncate all tables to keep test isolation
    tables = _db.metadata.sorted_tables
    for table in reversed(tables):
        _db.session.execute(table.delete())
    _db.session.commit()
    ctx.pop()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Domain fixtures — Tenant
# ---------------------------------------------------------------------------
@pytest.fixture
def tenant_a():
    """Primary test tenant."""
    t = Tenant(
        name='AutoShkolla Test A',
        slug='test-a',
        nui='123456789',
        email='testa@example.com',
        phone='044123456',
        address='Rr. Agim Ramadani',
        city='Prishtinë',
        is_active=True,
    )
    _db.session.add(t)
    _db.session.commit()
    return t


@pytest.fixture
def tenant_b():
    """Secondary test tenant for multi-tenant isolation tests."""
    t = Tenant(
        name='AutoShkolla Test B',
        slug='test-b',
        nui='987654321',
        email='testb@example.com',
        phone='044654321',
        address='Rr. Test B',
        city='Prizren',
        is_active=True,
    )
    _db.session.add(t)
    _db.session.commit()
    return t


# ---------------------------------------------------------------------------
# Domain fixtures — Users
# ---------------------------------------------------------------------------
@pytest.fixture
def admin_user(tenant_a):
    """Admin user for tenant A."""
    u = User(
        tenant_id=tenant_a.id,
        username='admin@test.com',
        full_name='Admin User',
        email='admin@test.com',
        role='administrator',
        is_active=True,
    )
    u.set_password('Test123!')
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def instructor_user(tenant_a):
    """Instructor user for tenant A."""
    u = User(
        tenant_id=tenant_a.id,
        username='instructor@test.com',
        full_name='Instructor User',
        email='instructor@test.com',
        role='instructor',
        is_active=True,
    )
    u.set_password('Test123!')
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def admin_user_b(tenant_b):
    """Admin user for tenant B — used for isolation tests."""
    u = User(
        tenant_id=tenant_b.id,
        username='adminb@test.com',
        full_name='Admin User B',
        email='adminb@test.com',
        role='administrator',
        is_active=True,
    )
    u.set_password('Test123!')
    _db.session.add(u)
    _db.session.commit()
    return u


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
@pytest.fixture
def admin_token(admin_user):
    """JWT access token for admin user."""
    return encode_access_token(
        str(admin_user.id), str(admin_user.tenant_id), admin_user.role
    )


@pytest.fixture
def instructor_token(instructor_user):
    """JWT access token for instructor user."""
    return encode_access_token(
        str(instructor_user.id), str(instructor_user.tenant_id), instructor_user.role
    )


@pytest.fixture
def admin_token_b(admin_user_b):
    """JWT access token for admin user of tenant B."""
    return encode_access_token(
        str(admin_user_b.id), str(admin_user_b.tenant_id), admin_user_b.role
    )


def auth_header(token: str) -> dict:
    """Helper to create Authorization header dict."""
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ---------------------------------------------------------------------------
# Domain fixtures — Category
# ---------------------------------------------------------------------------
@pytest.fixture
def category_b(tenant_a):
    """Category B license for tenant A."""
    c = Category(
        tenant_id=tenant_a.id,
        code='B',
        description='Automjete deri 3500kg',
        theory_hours=20,
        practical_hours=20,
        price=350.00,
        is_active=True,
    )
    _db.session.add(c)
    _db.session.commit()
    return c


@pytest.fixture
def category_b_tenant_b(tenant_b):
    """Category B for tenant B."""
    c = Category(
        tenant_id=tenant_b.id,
        code='B',
        description='Category B tenant B',
        theory_hours=20,
        practical_hours=20,
        price=300.00,
        is_active=True,
    )
    _db.session.add(c)
    _db.session.commit()
    return c


# ---------------------------------------------------------------------------
# Domain fixtures — Instructor
# ---------------------------------------------------------------------------
@pytest.fixture
def instructor(tenant_a):
    """Instructor for tenant A."""
    i = Instructor(
        tenant_id=tenant_a.id,
        code='I001',
        first_name='Filan',
        last_name='Fisteku',
        personal_number='1234567890',
        email='filan@test.com',
        phone='044111222',
        position='instructor',
        cost_per_candidate=65.00,
        is_active=True,
    )
    _db.session.add(i)
    _db.session.commit()
    return i


# ---------------------------------------------------------------------------
# Domain fixtures — Vehicle
# ---------------------------------------------------------------------------
@pytest.fixture
def vehicle(tenant_a, instructor):
    """Vehicle for tenant A assigned to instructor."""
    v = Vehicle(
        tenant_id=tenant_a.id,
        make='Volkswagen',
        model='Golf',
        plate_number='01-123-AA',
        chassis_number='VIN123456',
        instructor_id=instructor.id,
        is_active=True,
    )
    _db.session.add(v)
    _db.session.commit()
    return v


# ---------------------------------------------------------------------------
# Domain fixtures — Candidate
# ---------------------------------------------------------------------------
@pytest.fixture
def candidate(tenant_a, category_b, instructor):
    """Candidate for tenant A."""
    c = Candidate(
        tenant_id=tenant_a.id,
        code='1000000001',
        first_name='Arben',
        last_name='Krasniqi',
        personal_number='1100223344',
        phone='044333444',
        category_id=category_b.id,
        price=350.00,
        registration_date=date(2026, 1, 15),
        instructor_id=instructor.id,
        gender='M',
        is_archived=False,
    )
    _db.session.add(c)
    _db.session.commit()
    return c


@pytest.fixture
def candidate_b(tenant_b, category_b_tenant_b):
    """Candidate for tenant B — for isolation tests."""
    c = Candidate(
        tenant_id=tenant_b.id,
        code='2000000001',
        first_name='Besnik',
        last_name='Beqiri',
        personal_number='2200334455',
        phone='045555666',
        category_id=category_b_tenant_b.id,
        price=300.00,
        registration_date=date(2026, 2, 1),
        gender='M',
        is_archived=False,
    )
    _db.session.add(c)
    _db.session.commit()
    return c
