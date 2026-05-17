"""Integration tests for super admin API endpoints."""
import uuid
import pytest
from app.utils.db import db as _db
from app.models.tenant_model import Tenant
from app.models.user_model import User
from app.utils.jwt import encode_access_token
from tests.conftest import auth_header


@pytest.fixture
def super_admin_user(tenant_a):
    """Super admin user for testing."""
    u = User(
        tenant_id=tenant_a.id,
        username='superadmin@test.com',
        full_name='Super Admin',
        email='superadmin@test.com',
        role='super_admin',
        is_active=True,
    )
    u.set_password('Test123!')
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def super_admin_token(super_admin_user):
    """JWT for super admin."""
    return encode_access_token(
        str(super_admin_user.id), str(super_admin_user.tenant_id), super_admin_user.role
    )


class TestSuperAdminTenants:
    def test_list_tenants(self, client, super_admin_token, tenant_a):
        resp = client.get('/api/v1/superadmin/tenants', headers=auth_header(super_admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_list_tenants_search(self, client, super_admin_token, tenant_a):
        resp = client.get('/api/v1/superadmin/tenants?search=Test', headers=auth_header(super_admin_token))
        assert resp.status_code == 200

    def test_list_tenants_filter_active(self, client, super_admin_token, tenant_a):
        resp = client.get('/api/v1/superadmin/tenants?isActive=true', headers=auth_header(super_admin_token))
        assert resp.status_code == 200

    def test_get_tenant(self, client, super_admin_token, tenant_a):
        resp = client.get(f'/api/v1/superadmin/tenants/{tenant_a.id}', headers=auth_header(super_admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'statistics' in result

    def test_get_tenant_not_found(self, client, super_admin_token):
        resp = client.get(f'/api/v1/superadmin/tenants/{uuid.uuid4()}', headers=auth_header(super_admin_token))
        assert resp.status_code == 404

    def test_create_tenant(self, client, super_admin_token):
        resp = client.post('/api/v1/superadmin/tenants', headers=auth_header(super_admin_token), json={
            'name': 'New Tenant',
            'slug': 'new-tenant',
            'contactEmail': 'new@test.com',
            'contactPhone': '049111222',
            'address': 'Rr. Test',
        })
        assert resp.status_code == 201

    def test_create_tenant_duplicate_slug(self, client, super_admin_token, tenant_a):
        resp = client.post('/api/v1/superadmin/tenants', headers=auth_header(super_admin_token), json={
            'name': 'Duplicate',
            'slug': 'test-a',  # already exists
        })
        assert resp.status_code == 400

    def test_update_tenant(self, client, super_admin_token, tenant_a):
        resp = client.put(
            f'/api/v1/superadmin/tenants/{tenant_a.id}',
            headers=auth_header(super_admin_token),
            json={'name': 'Updated Tenant Name'},
        )
        assert resp.status_code == 200

    def test_update_tenant_not_found(self, client, super_admin_token):
        resp = client.put(
            f'/api/v1/superadmin/tenants/{uuid.uuid4()}',
            headers=auth_header(super_admin_token),
            json={'name': 'X'},
        )
        assert resp.status_code == 404

    def test_delete_tenant(self, client, super_admin_token, tenant_b):
        resp = client.delete(
            f'/api/v1/superadmin/tenants/{tenant_b.id}',
            headers=auth_header(super_admin_token),
        )
        assert resp.status_code == 204

    def test_delete_tenant_not_found(self, client, super_admin_token):
        resp = client.delete(
            f'/api/v1/superadmin/tenants/{uuid.uuid4()}',
            headers=auth_header(super_admin_token),
        )
        assert resp.status_code == 404

    def test_forbidden_for_regular_admin(self, client, admin_token):
        resp = client.get('/api/v1/superadmin/tenants', headers=auth_header(admin_token))
        assert resp.status_code == 403


class TestSuperAdminTenantUsers:
    def test_list_tenant_users(self, client, super_admin_token, tenant_a, admin_user):
        resp = client.get(
            f'/api/v1/superadmin/tenants/{tenant_a.id}/users',
            headers=auth_header(super_admin_token),
        )
        assert resp.status_code == 200

    def test_list_tenant_users_not_found(self, client, super_admin_token):
        resp = client.get(
            f'/api/v1/superadmin/tenants/{uuid.uuid4()}/users',
            headers=auth_header(super_admin_token),
        )
        assert resp.status_code == 404

    def test_create_tenant_user(self, client, super_admin_token, tenant_a):
        resp = client.post(
            f'/api/v1/superadmin/tenants/{tenant_a.id}/users',
            headers=auth_header(super_admin_token),
            json={
                'email': 'tenantuser@test.com',
                'password': 'TestPass123!',
                'fullName': 'Tenant User',
                'role': 'administrator',
            },
        )
        assert resp.status_code == 201

    def test_create_tenant_user_duplicate(self, client, super_admin_token, tenant_a, admin_user):
        resp = client.post(
            f'/api/v1/superadmin/tenants/{tenant_a.id}/users',
            headers=auth_header(super_admin_token),
            json={
                'email': 'admin@test.com',
                'password': 'TestPass123!',
                'fullName': 'Duplicate',
                'role': 'administrator',
            },
        )
        assert resp.status_code == 400


class TestSuperAdminImpersonate:
    def test_impersonate(self, client, super_admin_token, admin_user):
        resp = client.post('/api/v1/superadmin/impersonate', headers=auth_header(super_admin_token), json={
            'userId': str(admin_user.id),
        })
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'accessToken' in result

    def test_impersonate_not_found(self, client, super_admin_token):
        resp = client.post('/api/v1/superadmin/impersonate', headers=auth_header(super_admin_token), json={
            'userId': str(uuid.uuid4()),
        })
        assert resp.status_code == 404


class TestSuperAdminStats:
    def test_global_stats(self, client, super_admin_token, tenant_a, admin_user):
        resp = client.get('/api/v1/superadmin/stats', headers=auth_header(super_admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'totalTenants' in result
        assert 'totalUsers' in result
