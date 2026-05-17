"""Integration tests for instructor portal API endpoints."""
import uuid
import pytest
from app.utils.db import db as _db
from app.models.instructor_model import Instructor
from app.models.user_model import User
from app.utils.jwt import encode_access_token
from tests.conftest import auth_header


@pytest.fixture
def instructor_with_login(tenant_a):
    """Instructor with a linked user account for portal access."""
    u = User(
        tenant_id=tenant_a.id,
        username='portal_instructor@test.com',
        full_name='Portal Instructor',
        email='portal_instructor@test.com',
        role='instructor',
        is_active=True,
    )
    u.set_password('Test123!')
    _db.session.add(u)
    _db.session.flush()

    i = Instructor(
        tenant_id=tenant_a.id,
        code='IP01',
        first_name='Portal',
        last_name='Instructor',
        personal_number='9988776655',
        email='portal_instructor@test.com',
        phone='044777888',
        position='instructor',
        cost_per_candidate=65.00,
        is_active=True,
        user_id=u.id,
    )
    _db.session.add(i)
    _db.session.commit()
    return i


@pytest.fixture
def portal_token(instructor_with_login):
    """JWT token for instructor portal user."""
    return encode_access_token(
        str(instructor_with_login.user_id),
        str(instructor_with_login.tenant_id),
        'instructor',
    )


class TestInstructorPortal:
    def test_instructor_me(self, client, portal_token):
        resp = client.get('/api/v1/instructor/me', headers=auth_header(portal_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'activeCandidatesCount' in result
        assert 'outstandingDebt' in result

    def test_instructor_me_admin_forbidden(self, client, admin_token):
        resp = client.get('/api/v1/instructor/me', headers=auth_header(admin_token))
        assert resp.status_code == 403

    def test_instructor_candidates(self, client, portal_token):
        resp = client.get('/api/v1/instructor/candidates', headers=auth_header(portal_token))
        assert resp.status_code == 200

    def test_instructor_candidates_archived(self, client, portal_token):
        resp = client.get('/api/v1/instructor/candidates?archived=true', headers=auth_header(portal_token))
        assert resp.status_code == 200

    def test_instructor_calendar(self, client, portal_token):
        resp = client.get('/api/v1/instructor/calendar', headers=auth_header(portal_token))
        assert resp.status_code == 200

    def test_instructor_calendar_with_dates(self, client, portal_token):
        resp = client.get(
            '/api/v1/instructor/calendar?date_from=2026-03-01&date_to=2026-03-31',
            headers=auth_header(portal_token),
        )
        assert resp.status_code == 200

    def test_instructor_debt(self, client, portal_token):
        resp = client.get('/api/v1/instructor/debt', headers=auth_header(portal_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'totalAmountOwed' in result
        assert 'payments' in result

    def test_instructor_dashboard(self, client, portal_token):
        resp = client.get('/api/v1/instructor/dashboard', headers=auth_header(portal_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'activeCandidates' in result
        assert 'lessonsToday' in result
        assert 'outstandingDebt' in result
        assert 'unreadMessages' in result

    def test_instructor_dashboard_admin_forbidden(self, client, admin_token):
        resp = client.get('/api/v1/instructor/dashboard', headers=auth_header(admin_token))
        assert resp.status_code == 403
