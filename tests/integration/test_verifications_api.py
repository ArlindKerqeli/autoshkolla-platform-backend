"""Integration tests for verifications API endpoints."""
import uuid
import pytest
from app.utils.db import db as _db
from app.models.verification_model import Verification
from tests.conftest import auth_header


class TestVerifications:
    def test_list_verifications(self, client, admin_token, candidate):
        resp = client.get(
            f'/api/v1/verifications?candidateId={candidate.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_list_verifications_missing_candidate(self, client, admin_token):
        resp = client.get('/api/v1/verifications', headers=auth_header(admin_token))
        assert resp.status_code == 400

    def test_list_verifications_candidate_not_found(self, client, admin_token):
        resp = client.get(
            f'/api/v1/verifications?candidateId={uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_create_verification(self, client, admin_token, candidate, category_b, instructor):
        resp = client.post('/api/v1/verifications', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'categoryId': str(category_b.id),
            'verificationDate': '2026-03-01',
            'theoryHoursStart': '2026-01-15',
            'theoryHoursEnd': '2026-02-15',
            'practicalHoursStart': '2026-02-16',
            'practicalHoursEnd': '2026-03-15',
            'sequenceNumber': '001',
            'instructorId': str(instructor.id),
            'redCrossCert': True,
            'idCardCopy': True,
        })
        assert resp.status_code == 201

    def test_create_verification_candidate_not_found(self, client, admin_token, category_b):
        resp = client.post('/api/v1/verifications', headers=auth_header(admin_token), json={
            'candidateId': str(uuid.uuid4()),
            'categoryId': str(category_b.id),
        })
        assert resp.status_code == 404

    def test_create_verification_category_not_found(self, client, admin_token, candidate):
        resp = client.post('/api/v1/verifications', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'categoryId': str(uuid.uuid4()),
        })
        assert resp.status_code == 404

    def test_create_verification_forbidden(self, client, instructor_token, candidate, category_b):
        resp = client.post('/api/v1/verifications', headers=auth_header(instructor_token), json={
            'candidateId': str(candidate.id),
            'categoryId': str(category_b.id),
        })
        assert resp.status_code == 403

    def test_get_verification(self, client, admin_token, candidate, category_b):
        create_resp = client.post('/api/v1/verifications', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'categoryId': str(category_b.id),
        })
        v = create_resp.get_json()
        v_id = v.get('id') or v.get('data', {}).get('id')
        resp = client.get(f'/api/v1/verifications/{v_id}', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_get_verification_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/verifications/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_update_verification(self, client, admin_token, candidate, category_b):
        create_resp = client.post('/api/v1/verifications', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'categoryId': str(category_b.id),
        })
        v = create_resp.get_json()
        v_id = v.get('id') or v.get('data', {}).get('id')
        resp = client.put(
            f'/api/v1/verifications/{v_id}',
            headers=auth_header(admin_token),
            json={'sequenceNumber': '002', 'redCrossCert': True},
        )
        assert resp.status_code == 200

    def test_update_verification_not_found(self, client, admin_token):
        resp = client.put(
            f'/api/v1/verifications/{uuid.uuid4()}',
            headers=auth_header(admin_token),
            json={'sequenceNumber': '999'},
        )
        assert resp.status_code == 404

    def test_delete_verification(self, client, admin_token, candidate, category_b):
        create_resp = client.post('/api/v1/verifications', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'categoryId': str(category_b.id),
        })
        v = create_resp.get_json()
        v_id = v.get('id') or v.get('data', {}).get('id')
        resp = client.delete(f'/api/v1/verifications/{v_id}', headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_delete_verification_not_found(self, client, admin_token):
        resp = client.delete(f'/api/v1/verifications/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_delete_verification_forbidden(self, client, instructor_token, candidate, category_b):
        resp = client.delete(
            f'/api/v1/verifications/{uuid.uuid4()}',
            headers=auth_header(instructor_token),
        )
        assert resp.status_code == 403
