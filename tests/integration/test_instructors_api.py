"""Integration tests for instructors API endpoints."""
import uuid
import pytest

from tests.conftest import auth_header


class TestListInstructors:
    def test_list_instructors(self, client, admin_token, instructor):
        resp = client.get('/api/v1/instructors', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_list_instructors_filter_active(self, client, admin_token, instructor):
        resp = client.get(
            '/api/v1/instructors?active=true',
            headers=auth_header(admin_token),
        )
        data = resp.get_json()
        assert all(i['isActive'] for i in data['data'])

    def test_list_instructors_filter_position(self, client, admin_token, instructor):
        resp = client.get(
            '/api/v1/instructors?position=instructor',
            headers=auth_header(admin_token),
        )
        data = resp.get_json()
        assert all(i['position'] == 'instructor' for i in data['data'])


class TestGetInstructor:
    def test_get_instructor_success(self, client, admin_token, instructor):
        resp = client.get(
            f'/api/v1/instructors/{instructor.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['code'] == 'I001'

    def test_get_instructor_not_found(self, client, admin_token):
        resp = client.get(
            f'/api/v1/instructors/{uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404


class TestCreateInstructor:
    def _payload(self, code='I200'):
        return {
            'code': code,
            'firstName': 'Arta',
            'lastName': 'Hoxha',
            'personalNumber': '7788990011',
            'email': 'arta@test.com',
            'phone': '044777888',
            'position': 'instructor',
        }

    def test_create_instructor_success(self, client, admin_token):
        resp = client.post(
            '/api/v1/instructors',
            headers=auth_header(admin_token),
            json=self._payload(),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['data']['code'] == 'I200'
        assert data['data']['hasLogin'] is False

    def test_create_instructor_with_login(self, client, admin_token):
        payload = self._payload(code='I201')
        payload['password'] = 'Pass123!'
        resp = client.post(
            '/api/v1/instructors',
            headers=auth_header(admin_token),
            json=payload,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['data']['hasLogin'] is True

    def test_create_instructor_duplicate_code(self, client, admin_token, instructor):
        resp = client.post(
            '/api/v1/instructors',
            headers=auth_header(admin_token),
            json=self._payload(code='I001'),
        )
        assert resp.status_code == 400

    def test_create_instructor_forbidden_for_instructor_role(self, client, instructor_token):
        resp = client.post(
            '/api/v1/instructors',
            headers=auth_header(instructor_token),
            json=self._payload(),
        )
        assert resp.status_code == 403


class TestUpdateInstructor:
    def test_update_instructor(self, client, admin_token, instructor):
        resp = client.put(
            f'/api/v1/instructors/{instructor.id}',
            headers=auth_header(admin_token),
            json={'firstName': 'UpdatedFilan'},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['firstName'] == 'UpdatedFilan'


class TestDeleteInstructor:
    def test_delete_instructor(self, client, admin_token, instructor):
        resp = client.delete(
            f'/api/v1/instructors/{instructor.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 204
