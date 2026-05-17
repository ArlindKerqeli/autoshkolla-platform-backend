"""Unit tests for middleware modules."""
import pytest

from app.middleware.error_handler import (
    ValidationError, Unauthorized, Forbidden, NotFound,
)


class TestCustomExceptions:
    def test_validation_error(self):
        err = ValidationError('Bad input', details=[{'field': 'name', 'message': 'required'}])
        assert err.status_code == 400
        assert err.code == 'VALIDATION_ERROR'
        assert len(err.details) == 1

    def test_validation_error_no_details(self):
        err = ValidationError('Bad')
        assert err.details == []

    def test_unauthorized(self):
        err = Unauthorized('Not logged in')
        assert err.status_code == 401
        assert err.code == 'UNAUTHORIZED'
        assert str(err) == 'Not logged in'

    def test_unauthorized_default_message(self):
        err = Unauthorized()
        assert str(err) == 'Unauthorized'

    def test_forbidden(self):
        err = Forbidden('No access')
        assert err.status_code == 403
        assert err.code == 'FORBIDDEN'

    def test_not_found(self):
        err = NotFound('Resource missing')
        assert err.status_code == 404
        assert err.code == 'NOT_FOUND'


class TestErrorResponseFormat:
    def test_validation_error_response(self, client, admin_token):
        """Validation errors return proper JSON envelope."""
        from tests.conftest import auth_header
        # Send invalid candidate creation (missing required fields)
        resp = client.post(
            '/api/v1/candidates',
            headers=auth_header(admin_token),
            json={'firstName': 'Only'},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error']['code'] == 'VALIDATION_ERROR'

    def test_not_found_response(self, client, admin_token):
        import uuid
        from tests.conftest import auth_header
        resp = client.get(
            f'/api/v1/candidates/{uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404
        data = resp.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'NOT_FOUND'

    def test_unauthorized_response(self, client):
        resp = client.get('/api/v1/candidates')
        assert resp.status_code == 401
        data = resp.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'UNAUTHORIZED'


class TestResponseEnvelope:
    def test_success_response_wrapped(self, client, admin_token):
        from tests.conftest import auth_header
        resp = client.get('/api/v1/health')
        data = resp.get_json()
        assert data['success'] is True
        assert 'data' in data

    def test_error_response_not_double_wrapped(self, client):
        resp = client.get('/api/v1/candidates')  # No auth
        data = resp.get_json()
        assert data['success'] is False
        # Should not be wrapped in another envelope
        assert 'data' not in data
