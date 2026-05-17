"""Unit tests for SQLAlchemy models."""
import uuid
from datetime import date, datetime
from decimal import Decimal

from app.utils.db import db as _db
from app.models.tenant_model import Tenant
from app.models.user_model import User
from app.models.category_model import Category
from app.models.instructor_model import Instructor
from app.models.vehicle_model import Vehicle
from app.models.candidate_model import Candidate
from app.models.instructor_payment_model import InstructorPayment


# ---------------------------------------------------------------------------
# Tenant model
# ---------------------------------------------------------------------------
class TestTenantModel:
    def test_create_tenant(self, tenant_a):
        assert tenant_a.name == 'AutoShkolla Test A'
        assert tenant_a.slug == 'test-a'
        assert tenant_a.is_active is True
        assert tenant_a.id is not None

    def test_tenant_to_dict(self, tenant_a):
        d = tenant_a.to_dict()
        assert d['name'] == 'AutoShkolla Test A'
        assert d['slug'] == 'test-a'
        assert d['isActive'] is True
        assert 'id' in d
        assert 'createdAt' in d

    def test_tenant_repr(self, tenant_a):
        assert 'AutoShkolla Test A' in repr(tenant_a)


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------
class TestUserModel:
    def test_create_user(self, admin_user):
        assert admin_user.username == 'admin@test.com'
        assert admin_user.role == 'administrator'
        assert admin_user.is_active is True

    def test_set_password_and_check(self, tenant_a):
        u = User(
            tenant_id=tenant_a.id,
            username='pwtest',
            full_name='PW Test',
            role='administrator',
        )
        u.set_password('MySecret123')
        assert u.password_hash is not None
        assert u.password_hash != 'MySecret123'
        assert u.check_password('MySecret123') is True
        assert u.check_password('wrong') is False

    def test_user_to_dict(self, admin_user):
        d = admin_user.to_dict()
        assert d['username'] == 'admin@test.com'
        assert d['role'] == 'administrator'
        assert d['isActive'] is True
        assert 'password_hash' not in d
        assert 'passwordHash' not in d

    def test_user_to_dict_with_tenant(self, admin_user):
        d = admin_user.to_dict(include_tenant=True)
        assert 'tenant' in d
        assert d['tenant']['slug'] == 'test-a'

    def test_user_repr(self, admin_user):
        assert 'admin@test.com' in repr(admin_user)

    def test_valid_roles(self):
        assert 'super_admin' in User.VALID_ROLES
        assert 'administrator' in User.VALID_ROLES
        assert 'instructor' in User.VALID_ROLES
        assert 'lecturer' in User.VALID_ROLES


# ---------------------------------------------------------------------------
# Category model
# ---------------------------------------------------------------------------
class TestCategoryModel:
    def test_create_category(self, category_b):
        assert category_b.code == 'B'
        assert category_b.theory_hours == 20
        assert category_b.practical_hours == 20
        assert float(category_b.price) == 350.00

    def test_category_to_dict(self, category_b):
        d = category_b.to_dict()
        assert d['code'] == 'B'
        assert d['theoryHours'] == 20
        assert d['price'] == 350.00
        assert d['isActive'] is True


# ---------------------------------------------------------------------------
# Instructor model
# ---------------------------------------------------------------------------
class TestInstructorModel:
    def test_create_instructor(self, instructor):
        assert instructor.code == 'I001'
        assert instructor.first_name == 'Filan'
        assert instructor.last_name == 'Fisteku'
        assert instructor.position == 'instructor'

    def test_instructor_full_name(self, instructor):
        assert instructor.full_name == 'Filan Fisteku'

    def test_instructor_to_dict(self, instructor):
        d = instructor.to_dict()
        assert d['code'] == 'I001'
        assert d['fullName'] == 'Filan Fisteku'
        assert d['costPerCandidate'] == 65.00
        assert d['hasLogin'] is False

    def test_valid_positions(self):
        assert 'instructor' in Instructor.VALID_POSITIONS
        assert 'lecturer' in Instructor.VALID_POSITIONS
        assert 'both' in Instructor.VALID_POSITIONS


# ---------------------------------------------------------------------------
# Vehicle model
# ---------------------------------------------------------------------------
class TestVehicleModel:
    def test_create_vehicle(self, vehicle):
        assert vehicle.make == 'Volkswagen'
        assert vehicle.plate_number == '01-123-AA'
        assert vehicle.is_active is True

    def test_vehicle_to_dict(self, vehicle):
        d = vehicle.to_dict()
        assert d['make'] == 'Volkswagen'
        assert d['plateNumber'] == '01-123-AA'
        assert d['instructorName'] == 'Filan Fisteku'


# ---------------------------------------------------------------------------
# Candidate model
# ---------------------------------------------------------------------------
class TestCandidateModel:
    def test_create_candidate(self, candidate):
        assert candidate.first_name == 'Arben'
        assert candidate.last_name == 'Krasniqi'
        assert candidate.personal_number == '1100223344'

    def test_candidate_full_name(self, candidate):
        assert candidate.full_name == 'Arben Krasniqi'

    def test_candidate_debt(self, candidate):
        assert candidate.debt == 350.00

    def test_candidate_debt_partial_payment(self, candidate):
        candidate.amount_paid = Decimal('100.00')
        _db.session.flush()
        assert candidate.debt == 250.00

    def test_candidate_to_dict_summary(self, candidate):
        d = candidate.to_dict(summary=True)
        assert d['fullName'] == 'Arben Krasniqi'
        assert d['debt'] == 350.00
        assert 'dateOfBirth' not in d

    def test_candidate_to_dict_full(self, candidate):
        d = candidate.to_dict(summary=False)
        assert 'dateOfBirth' in d
        assert 'gender' in d
        assert d['gender'] == 'M'


# ---------------------------------------------------------------------------
# InstructorPayment model
# ---------------------------------------------------------------------------
class TestInstructorPaymentModel:
    def test_create_instructor_payment(self, tenant_a, instructor, candidate):
        ip = InstructorPayment(
            tenant_id=tenant_a.id,
            instructor_id=instructor.id,
            candidate_id=candidate.id,
            amount=65.00,
            status='unpaid',
        )
        _db.session.add(ip)
        _db.session.flush()
        assert ip.id is not None
        assert ip.status == 'unpaid'

    def test_outstanding_property(self, tenant_a, instructor, candidate):
        ip = InstructorPayment(
            tenant_id=tenant_a.id,
            instructor_id=instructor.id,
            candidate_id=candidate.id,
            amount=65.00,
            amount_paid=20.00,
            status='partial',
        )
        _db.session.add(ip)
        _db.session.flush()
        assert ip.outstanding == 45.00

    def test_to_dict(self, tenant_a, instructor, candidate):
        ip = InstructorPayment(
            tenant_id=tenant_a.id,
            instructor_id=instructor.id,
            candidate_id=candidate.id,
            amount=65.00,
            amount_paid=0,
            status='unpaid',
        )
        _db.session.add(ip)
        _db.session.flush()
        d = ip.to_dict()
        assert d['amount'] == 65.00
        assert d['outstanding'] == 65.00
        assert d['status'] == 'unpaid'
        assert d['candidateName'] == 'Arben Krasniqi'
