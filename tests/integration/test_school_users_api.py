"""Integration tests for school profile, users, and dashboard API endpoints."""
import uuid
import pytest
from tests.conftest import auth_header


# ---------------------------------------------------------------------------
# School Profile
# ---------------------------------------------------------------------------
class TestSchoolProfile:
    def test_get_school_profile(self, client, admin_token):
        resp = client.get('/api/v1/school/profile', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['slug'] == 'test-a'

    def test_update_school_profile(self, client, admin_token):
        resp = client.put('/api/v1/school/profile', headers=auth_header(admin_token), json={
            'name': 'Updated School Name',
        })
        assert resp.status_code == 200
        assert resp.get_json()['data']['name'] == 'Updated School Name'


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class TestListUsers:
    def test_list_users(self, client, admin_token):
        resp = client.get('/api/v1/users', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.get_json()['success'] is True

    def test_list_users_instructor_forbidden(self, client, instructor_token):
        resp = client.get('/api/v1/users', headers=auth_header(instructor_token))
        assert resp.status_code == 403


class TestCreateUser:
    def test_create_user(self, client, admin_token):
        resp = client.post('/api/v1/users', headers=auth_header(admin_token), json={
            'email': 'newuser@test.com',
            'fullName': 'New User',
            'password': 'NewPass123!',
            'role': 'administrator',
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['username'] == 'newuser@test.com'


class TestUpdateUser:
    def test_update_user(self, client, admin_token, admin_user):
        resp = client.put(
            f'/api/v1/users/{admin_user.id}',
            headers=auth_header(admin_token),
            json={'fullName': 'Updated Admin'},
        )
        assert resp.status_code == 200
        assert resp.get_json()['data']['fullName'] == 'Updated Admin'


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class TestDashboard:
    def test_dashboard_stats(self, client, admin_token, candidate):
        resp = client.get('/api/v1/dashboard/stats', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_dashboard_category_breakdown(self, client, admin_token, candidate):
        resp = client.get('/api/v1/dashboard/category-breakdown', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_dashboard_today_schedule(self, client, admin_token):
        resp = client.get('/api/v1/dashboard/today-schedule', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_dashboard_alerts(self, client, admin_token):
        resp = client.get('/api/v1/dashboard/alerts', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_dashboard_instructor_forbidden(self, client, instructor_token):
        resp = client.get('/api/v1/dashboard/stats', headers=auth_header(instructor_token))
        assert resp.status_code == 403
