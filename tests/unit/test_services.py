"""Unit tests for service layer."""
import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.services.auth_service import AuthService
from app.services.candidate_service import CandidateService
from app.services.instructor_service import InstructorService
from app.middleware.error_handler import (
    Unauthorized, NotFound, ValidationError, Forbidden,
)
from app.utils.db import db as _db
from app.models.user_model import User
from app.models.candidate_model import Candidate
from app.models.instructor_model import Instructor
from app.models.instructor_payment_model import InstructorPayment


# ---------------------------------------------------------------------------
# AuthService
# ---------------------------------------------------------------------------
class TestAuthService:
    def test_login_success(self, admin_user):
        svc = AuthService()
        result = svc.login('admin@test.com', 'Test123!')
        assert 'accessToken' in result
        assert 'refreshToken' in result
        assert result['user']['username'] == 'admin@test.com'

    def test_login_wrong_password(self, admin_user):
        svc = AuthService()
        with pytest.raises(Unauthorized, match='Invalid username or password'):
            svc.login('admin@test.com', 'wrong')

    def test_login_nonexistent_user(self, tenant_a):
        svc = AuthService()
        with pytest.raises(Unauthorized, match='Invalid username or password'):
            svc.login('nobody@test.com', 'pass')

    def test_login_inactive_user(self, tenant_a):
        u = User(
            tenant_id=tenant_a.id,
            username='inactive@test.com',
            full_name='Inactive',
            role='administrator',
            is_active=False,
        )
        u.set_password('Test123!')
        _db.session.add(u)
        _db.session.flush()

        svc = AuthService()
        with pytest.raises(Unauthorized, match='Invalid username or password'):
            svc.login('inactive@test.com', 'Test123!')

    def test_login_inactive_tenant(self, tenant_a):
        tenant_a.is_active = False
        _db.session.flush()
        u = User(
            tenant_id=tenant_a.id,
            username='tenantoff@test.com',
            full_name='Tenant Off',
            role='administrator',
            is_active=True,
        )
        u.set_password('Test123!')
        _db.session.add(u)
        _db.session.flush()
        svc = AuthService()
        with pytest.raises(Unauthorized, match='Tenant is inactive'):
            svc.login('tenantoff@test.com', 'Test123!')

    def test_refresh_success(self, admin_user):
        svc = AuthService()
        login_result = svc.login('admin@test.com', 'Test123!')
        refresh_result = svc.refresh(login_result['refreshToken'])
        assert 'accessToken' in refresh_result

    def test_refresh_invalid_token(self, tenant_a):
        svc = AuthService()
        with pytest.raises(Unauthorized, match='Invalid refresh token'):
            svc.refresh('invalid.token.here')

    def test_get_me(self, admin_user):
        svc = AuthService()
        result = svc.get_me(str(admin_user.id), str(admin_user.tenant_id))
        assert result['username'] == 'admin@test.com'

    def test_get_me_not_found(self, tenant_a):
        svc = AuthService()
        with pytest.raises(NotFound, match='User not found'):
            svc.get_me(str(uuid.uuid4()), str(tenant_a.id))


# ---------------------------------------------------------------------------
# CandidateService
# ---------------------------------------------------------------------------
class TestCandidateService:
    def _candidate_data(self, category_id, instructor_id=None):
        data = {
            'firstName': 'Test',
            'lastName': 'Kandidat',
            'personalNumber': '9900112233',
            'categoryId': str(category_id),
            'price': 350,
            'registrationDate': date(2026, 3, 1),
        }
        if instructor_id:
            data['instructorId'] = str(instructor_id)
        return data

    def test_generate_code_first(self, tenant_a):
        svc = CandidateService()
        code = svc.generate_code(str(tenant_a.id))
        assert code == '1000000001'

    def test_generate_code_increments(self, candidate):
        svc = CandidateService()
        code = svc.generate_code(str(candidate.tenant_id))
        assert code == '1000000002'

    def test_create_candidate(self, tenant_a, category_b):
        svc = CandidateService()
        data = self._candidate_data(category_b.id)
        c = svc.create_candidate(str(tenant_a.id), data)
        assert c.id is not None
        assert c.first_name == 'Test'
        assert c.personal_number == '9900112233'

    def test_create_candidate_with_instructor(self, tenant_a, category_b, instructor):
        svc = CandidateService()
        data = self._candidate_data(category_b.id, instructor.id)
        c = svc.create_candidate(str(tenant_a.id), data)
        assert c.instructor_id == instructor.id
        ip = InstructorPayment.query.filter_by(
            instructor_id=instructor.id, candidate_id=c.id
        ).first()
        assert ip is not None
        assert float(ip.amount) == 65.00

    def test_create_candidate_invalid_gender(self, tenant_a, category_b):
        svc = CandidateService()
        data = self._candidate_data(category_b.id)
        data['gender'] = 'X'
        with pytest.raises(ValidationError, match='Gender'):
            svc.create_candidate(str(tenant_a.id), data)

    def test_update_candidate(self, candidate):
        svc = CandidateService()
        updated = svc.update_candidate(
            str(candidate.tenant_id), str(candidate.id),
            {'firstName': 'Updated'}
        )
        assert updated.first_name == 'Updated'

    def test_update_candidate_not_found(self, tenant_a):
        svc = CandidateService()
        with pytest.raises(NotFound, match='Candidate not found'):
            svc.update_candidate(str(tenant_a.id), str(uuid.uuid4()), {'firstName': 'X'})

    def test_soft_delete(self, candidate):
        svc = CandidateService()
        svc.soft_delete(str(candidate.tenant_id), str(candidate.id))
        assert candidate.deleted_at is not None

    def test_soft_delete_not_found(self, tenant_a):
        svc = CandidateService()
        with pytest.raises(NotFound, match='Candidate not found'):
            svc.soft_delete(str(tenant_a.id), str(uuid.uuid4()))

    def test_archive(self, candidate):
        svc = CandidateService()
        result = svc.archive(str(candidate.tenant_id), str(candidate.id))
        assert result.is_archived is True

    def test_archive_not_found(self, tenant_a):
        svc = CandidateService()
        with pytest.raises(NotFound, match='Candidate not found'):
            svc.archive(str(tenant_a.id), str(uuid.uuid4()))


# ---------------------------------------------------------------------------
# InstructorService
# ---------------------------------------------------------------------------
class TestInstructorService:
    def _instructor_data(self, code='I100'):
        return {
            'code': code,
            'firstName': 'Ilir',
            'lastName': 'Gashi',
            'personalNumber': '5566778899',
            'email': 'ilir@test.com',
            'phone': '044999888',
            'position': 'instructor',
        }

    def test_create_instructor(self, tenant_a):
        svc = InstructorService()
        data = self._instructor_data()
        i = svc.create_instructor(str(tenant_a.id), data)
        assert i.id is not None
        assert i.code == 'I100'
        assert i.user_id is None

    def test_create_instructor_with_login(self, tenant_a):
        svc = InstructorService()
        data = self._instructor_data(code='I101')
        data['password'] = 'Secret123!'
        i = svc.create_instructor(str(tenant_a.id), data)
        assert i.user_id is not None
        user = User.query.get(i.user_id)
        assert user.role == 'instructor'
        assert user.check_password('Secret123!')

    def test_create_instructor_duplicate_code(self, tenant_a, instructor):
        svc = InstructorService()
        data = self._instructor_data(code='I001')
        with pytest.raises(ValidationError, match='already exists'):
            svc.create_instructor(str(tenant_a.id), data)

    def test_create_instructor_invalid_position(self, tenant_a):
        svc = InstructorService()
        data = self._instructor_data()
        data['position'] = 'invalid'
        with pytest.raises(ValidationError, match='Invalid position'):
            svc.create_instructor(str(tenant_a.id), data)

    def test_update_instructor(self, instructor):
        svc = InstructorService()
        updated = svc.update_instructor(
            str(instructor.tenant_id), str(instructor.id),
            {'firstName': 'UpdatedName'}
        )
        assert updated.first_name == 'UpdatedName'

    def test_update_instructor_not_found(self, tenant_a):
        svc = InstructorService()
        with pytest.raises(NotFound, match='Instructor not found'):
            svc.update_instructor(str(tenant_a.id), str(uuid.uuid4()), {'firstName': 'X'})

    def test_delete_instructor(self, instructor):
        svc = InstructorService()
        svc.delete_instructor(str(instructor.tenant_id), str(instructor.id))
        assert instructor.is_active is False

    def test_delete_instructor_with_user(self, tenant_a):
        svc = InstructorService()
        data = self._instructor_data(code='I102')
        data['password'] = 'Pass123!'
        i = svc.create_instructor(str(tenant_a.id), data)
        svc.delete_instructor(str(tenant_a.id), str(i.id))
        assert i.is_active is False
        user = User.query.get(i.user_id)
        assert user.is_active is False

    def test_get_instructor_for_user(self, tenant_a):
        svc = InstructorService()
        data = self._instructor_data(code='I103')
        data['password'] = 'Pass123!'
        i = svc.create_instructor(str(tenant_a.id), data)
        found = svc.get_instructor_for_user(str(i.user_id), str(tenant_a.id))
        assert found.id == i.id

    def test_get_instructor_for_user_not_found(self, tenant_a):
        svc = InstructorService()
        with pytest.raises(NotFound, match='Instructor profile not found'):
            svc.get_instructor_for_user(str(uuid.uuid4()), str(tenant_a.id))
