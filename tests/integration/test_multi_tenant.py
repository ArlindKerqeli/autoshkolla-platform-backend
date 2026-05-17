"""Integration tests for multi-tenant isolation.

Verifies that data from one tenant is never accessible by another tenant's user.
"""
import uuid
import pytest

from tests.conftest import auth_header


class TestCandidateIsolation:
    def test_tenant_a_cannot_see_tenant_b_candidates(
        self, client, admin_token, candidate, candidate_b
    ):
        """Admin of tenant A should only see tenant A candidates."""
        resp = client.get('/api/v1/candidates', headers=auth_header(admin_token))
        data = resp.get_json()
        ids = [c['id'] for c in data['data']]
        # Should contain tenant A candidate
        assert str(candidate.id) in [str(i) for i in ids]
        # Should NOT contain tenant B candidate
        assert str(candidate_b.id) not in [str(i) for i in ids]

    def test_tenant_b_cannot_see_tenant_a_candidates(
        self, client, admin_token_b, candidate, candidate_b
    ):
        """Admin of tenant B should only see tenant B candidates."""
        resp = client.get('/api/v1/candidates', headers=auth_header(admin_token_b))
        data = resp.get_json()
        ids = [str(c['id']) for c in data['data']]
        assert str(candidate_b.id) in ids
        assert str(candidate.id) not in ids

    def test_tenant_a_cannot_get_tenant_b_candidate_by_id(
        self, client, admin_token, candidate_b
    ):
        """Admin of tenant A cannot fetch tenant B's candidate by ID."""
        resp = client.get(
            f'/api/v1/candidates/{candidate_b.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_tenant_b_cannot_update_tenant_a_candidate(
        self, client, admin_token_b, candidate
    ):
        """Admin of tenant B cannot update tenant A's candidate."""
        resp = client.put(
            f'/api/v1/candidates/{candidate.id}',
            headers=auth_header(admin_token_b),
            json={'firstName': 'Hacked'},
        )
        assert resp.status_code == 404

    def test_tenant_b_cannot_delete_tenant_a_candidate(
        self, client, admin_token_b, candidate
    ):
        """Admin of tenant B cannot delete tenant A's candidate."""
        resp = client.delete(
            f'/api/v1/candidates/{candidate.id}',
            headers=auth_header(admin_token_b),
        )
        assert resp.status_code == 404


class TestInstructorIsolation:
    def test_tenant_a_cannot_see_tenant_b_instructors(
        self, client, admin_token, admin_token_b, instructor
    ):
        """Tenant A instructors should not appear in tenant B listing."""
        resp_a = client.get('/api/v1/instructors', headers=auth_header(admin_token))
        resp_b = client.get('/api/v1/instructors', headers=auth_header(admin_token_b))
        ids_a = [str(i['id']) for i in resp_a.get_json()['data']]
        ids_b = [str(i['id']) for i in resp_b.get_json()['data']]
        assert str(instructor.id) in ids_a
        assert str(instructor.id) not in ids_b

    def test_tenant_b_cannot_get_tenant_a_instructor(
        self, client, admin_token_b, instructor
    ):
        resp = client.get(
            f'/api/v1/instructors/{instructor.id}',
            headers=auth_header(admin_token_b),
        )
        assert resp.status_code == 404
