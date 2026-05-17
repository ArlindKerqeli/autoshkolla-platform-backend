"""Integration tests for auth API endpoints."""
import json
import pytest

from tests.conftest import auth_header


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get('/api/v1/health')
        assert resp.status_code == 200


class TestLoginEndpoint:
    def test_login_success(self, client, admin_user):
        resp = client.post('/api/v1/auth/login', json={
            'username': 'admin@test.com',
            'password': 'Test123!',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'accessToken' in data['data']
        assert 'refreshToken' in data['data']
        assert data['data']['user']['username'] == 'admin@test.com'

    def test_login_wrong_password(self, client, admin_user):
        resp = client.post('/api/v1/auth/login', json={
            'username': 'admin@test.com',
            'password': 'wrong',
        })
        assert resp.status_code == 401
        data = resp.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'UNAUTHORIZED'

    def test_login_missing_fields(self, client):
        resp = client.post('/api/v1/auth/login', json={'username': 'admin@test.com'})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['success'] is False

    def test_login_empty_body(self, client):
        resp = client.post('/api/v1/auth/login', json={})
        assert resp.status_code == 400


class TestRefreshEndpoint:
    def test_refresh_success(self, client, admin_user):
        # First login to get refresh token
        login_resp = client.post('/api/v1/auth/login', json={
            'username': 'admin@test.com',
            'password': 'Test123!',
        })
        refresh_token = login_resp.get_json()['data']['refreshToken']

        resp = client.post('/api/v1/auth/refresh', json={
            'refreshToken': refresh_token,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'accessToken' in data['data']

    def test_refresh_invalid_token(self, client):
        resp = client.post('/api/v1/auth/refresh', json={
            'refreshToken': 'invalid.token',
        })
        assert resp.status_code == 401


class TestLogoutEndpoint:
    def test_logout_success(self, client, admin_token):
        resp = client.post('/api/v1/auth/logout', headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_logout_unauthenticated(self, client):
        resp = client.post('/api/v1/auth/logout')
        assert resp.status_code == 401


class TestMeEndpoint:
    def test_me_success(self, client, admin_token):
        resp = client.get('/api/v1/auth/me', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'admin@test.com'
        assert data['data']['role'] == 'administrator'

    def test_me_unauthenticated(self, client):
        resp = client.get('/api/v1/auth/me')
        assert resp.status_code == 401


class TestAuthGuard:
    def test_protected_route_no_token(self, client):
        resp = client.get('/api/v1/candidates')
        assert resp.status_code == 401

    def test_protected_route_invalid_token(self, client):
        resp = client.get('/api/v1/candidates', headers=auth_header('bad.token'))
        assert resp.status_code == 401

    def test_public_routes_no_auth(self, client):
        # Health should work without auth
        assert client.get('/api/v1/health').status_code == 200
        # Login should work without auth (even if body is bad, shouldn't be 401)
        resp = client.post('/api/v1/auth/login', json={})
        assert resp.status_code != 401
