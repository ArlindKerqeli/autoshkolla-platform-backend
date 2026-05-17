"""Integration tests for vehicles API endpoints."""
import uuid
import pytest
from tests.conftest import auth_header


class TestListVehicles:
    def test_list_vehicles(self, client, admin_token, vehicle):
        resp = client.get('/api/v1/vehicles', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_list_vehicles_filter_active(self, client, admin_token, vehicle):
        resp = client.get('/api/v1/vehicles?active=true', headers=auth_header(admin_token))
        data = resp.get_json()
        assert all(v['isActive'] for v in data['data'])


class TestGetVehicle:
    def test_get_vehicle_success(self, client, admin_token, vehicle):
        resp = client.get(f'/api/v1/vehicles/{vehicle.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.get_json()['data']['plateNumber'] == '01-123-AA'

    def test_get_vehicle_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/vehicles/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404


class TestCreateVehicle:
    def test_create_vehicle(self, client, admin_token):
        resp = client.post('/api/v1/vehicles', headers=auth_header(admin_token), json={
            'make': 'Toyota', 'plateNumber': '02-456-BB',
        })
        assert resp.status_code == 201
        assert resp.get_json()['data']['make'] == 'Toyota'

    def test_create_vehicle_instructor_forbidden(self, client, instructor_token):
        resp = client.post('/api/v1/vehicles', headers=auth_header(instructor_token), json={
            'make': 'Toyota', 'plateNumber': '02-456-BB',
        })
        assert resp.status_code == 403


class TestUpdateVehicle:
    def test_update_vehicle(self, client, admin_token, vehicle):
        resp = client.put(f'/api/v1/vehicles/{vehicle.id}', headers=auth_header(admin_token), json={
            'make': 'Audi',
        })
        assert resp.status_code == 200
        assert resp.get_json()['data']['make'] == 'Audi'

    def test_update_vehicle_not_found(self, client, admin_token):
        resp = client.put(f'/api/v1/vehicles/{uuid.uuid4()}', headers=auth_header(admin_token), json={'make': 'X'})
        assert resp.status_code == 404


class TestDeleteVehicle:
    def test_delete_vehicle(self, client, admin_token, vehicle):
        resp = client.delete(f'/api/v1/vehicles/{vehicle.id}', headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_delete_vehicle_not_found(self, client, admin_token):
        resp = client.delete(f'/api/v1/vehicles/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404
