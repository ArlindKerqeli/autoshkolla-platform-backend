"""Integration tests for categories API endpoints."""
import uuid
import pytest
from tests.conftest import auth_header


class TestListCategories:
    def test_list_categories(self, client, admin_token, category_b):
        resp = client.get('/api/v1/categories', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1


class TestGetCategory:
    def test_get_category_success(self, client, admin_token, category_b):
        resp = client.get(f'/api/v1/categories/{category_b.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.get_json()['data']['code'] == 'B'

    def test_get_category_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/categories/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404


class TestCreateCategory:
    def test_create_category(self, client, admin_token):
        resp = client.post('/api/v1/categories', headers=auth_header(admin_token), json={
            'code': 'C', 'description': 'Category C',
            'theoryHours': 30, 'practicalHours': 30, 'price': 500.00,
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['code'] == 'C'

    def test_create_category_instructor_forbidden(self, client, instructor_token):
        resp = client.post('/api/v1/categories', headers=auth_header(instructor_token), json={
            'code': 'C', 'description': 'C', 'theoryHours': 30, 'practicalHours': 30, 'price': 500,
        })
        assert resp.status_code == 403


class TestUpdateCategory:
    def test_update_category(self, client, admin_token, category_b):
        resp = client.put(f'/api/v1/categories/{category_b.id}', headers=auth_header(admin_token), json={
            'description': 'Updated B description',
        })
        assert resp.status_code == 200
        assert resp.get_json()['data']['description'] == 'Updated B description'


class TestDeleteCategory:
    def test_delete_category(self, client, admin_token, category_b):
        resp = client.delete(f'/api/v1/categories/{category_b.id}', headers=auth_header(admin_token))
        assert resp.status_code == 204
