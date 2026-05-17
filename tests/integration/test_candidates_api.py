"""Integration tests for candidates API endpoints."""
import uuid
import json
from datetime import date

import pytest

from tests.conftest import auth_header


class TestListCandidates:
    def test_list_candidates(self, client, admin_token, candidate):
        resp = client.get('/api/v1/candidates', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert len(data['data']) >= 1

    def test_list_candidates_search(self, client, admin_token, candidate):
        resp = client.get(
            '/api/v1/candidates?search=Arben',
            headers=auth_header(admin_token),
        )
        data = resp.get_json()
        assert data['success'] is True
        assert any(c['firstName'] == 'Arben' for c in data['data'])

    def test_list_candidates_filter_gender(self, client, admin_token, candidate):
        resp = client.get(
            '/api/v1/candidates?gender=M',
            headers=auth_header(admin_token),
        )
        data = resp.get_json()
        assert all(c.get('gender', 'M') == 'M' or 'gender' not in c for c in data['data'])

    def test_list_candidates_unauthenticated(self, client):
        resp = client.get('/api/v1/candidates')
        assert resp.status_code == 401


class TestGetCandidate:
    def test_get_candidate_success(self, client, admin_token, candidate):
        resp = client.get(
            f'/api/v1/candidates/{candidate.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['firstName'] == 'Arben'
        assert data['data']['lastName'] == 'Krasniqi'
        # Full detail should include dateOfBirth
        assert 'dateOfBirth' in data['data']

    def test_get_candidate_not_found(self, client, admin_token):
        resp = client.get(
            f'/api/v1/candidates/{uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404


class TestCreateCandidate:
    def _payload(self, category_id):
        return {
            'firstName': 'Rina',
            'lastName': 'Berisha',
            'personalNumber': '3300445566',
            'categoryId': str(category_id),
            'price': 350,
            'registrationDate': '2026-03-01',
        }

    def test_create_candidate_success(self, client, admin_token, category_b):
        resp = client.post(
            '/api/v1/candidates',
            headers=auth_header(admin_token),
            json=self._payload(category_b.id),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['data']['firstName'] == 'Rina'
        assert data['data']['id'] is not None

    def test_create_candidate_instructor_forbidden(self, client, instructor_token, category_b):
        resp = client.post(
            '/api/v1/candidates',
            headers=auth_header(instructor_token),
            json=self._payload(category_b.id),
        )
        assert resp.status_code == 403

    def test_create_candidate_missing_fields(self, client, admin_token):
        resp = client.post(
            '/api/v1/candidates',
            headers=auth_header(admin_token),
            json={'firstName': 'Only'},
        )
        assert resp.status_code == 400


class TestUpdateCandidate:
    def test_update_candidate_success(self, client, admin_token, candidate):
        resp = client.put(
            f'/api/v1/candidates/{candidate.id}',
            headers=auth_header(admin_token),
            json={'firstName': 'ArbenUpdated'},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['firstName'] == 'ArbenUpdated'

    def test_update_candidate_not_found(self, client, admin_token):
        resp = client.put(
            f'/api/v1/candidates/{uuid.uuid4()}',
            headers=auth_header(admin_token),
            json={'firstName': 'X'},
        )
        assert resp.status_code == 404

    def test_update_candidate_instructor_forbidden(self, client, instructor_token, candidate):
        resp = client.put(
            f'/api/v1/candidates/{candidate.id}',
            headers=auth_header(instructor_token),
            json={'firstName': 'Blocked'},
        )
        assert resp.status_code == 403


class TestDeleteCandidate:
    def test_delete_candidate_success(self, client, admin_token, candidate):
        resp = client.delete(
            f'/api/v1/candidates/{candidate.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 204

    def test_delete_candidate_not_found(self, client, admin_token):
        resp = client.delete(
            f'/api/v1/candidates/{uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404


class TestArchiveCandidate:
    def test_archive_candidate_success(self, client, admin_token, candidate):
        resp = client.post(
            f'/api/v1/candidates/{candidate.id}/archive',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['data']['isArchived'] is True

    def test_archive_candidate_instructor_forbidden(self, client, instructor_token, candidate):
        resp = client.post(
            f'/api/v1/candidates/{candidate.id}/archive',
            headers=auth_header(instructor_token),
        )
        assert resp.status_code == 403
