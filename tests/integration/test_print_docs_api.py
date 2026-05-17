"""Integration tests for print/PDF document endpoints."""
import uuid
import pytest
from tests.conftest import auth_header


class TestPrintDocs:
    def test_print_invoice(self, client, admin_token, candidate):
        resp = client.get(f'/api/v1/print/invoice/{candidate.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_print_invoice_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/print/invoice/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_print_registration_form(self, client, admin_token, candidate):
        resp = client.get(f'/api/v1/print/registration-form/{candidate.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_print_registration_form_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/print/registration-form/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_print_logbook(self, client, admin_token, candidate):
        resp = client.get(f'/api/v1/print/logbook/{candidate.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_print_contract(self, client, admin_token, candidate):
        resp = client.get(f'/api/v1/print/contract/{candidate.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_print_test_result(self, client, admin_token, candidate):
        resp = client.get(f'/api/v1/print/test-result/{candidate.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_print_certificate(self, client, admin_token, candidate):
        resp = client.get(f'/api/v1/print/certificate/{candidate.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'

    def test_print_candidate_list(self, client, admin_token):
        resp = client.get('/api/v1/print/candidate-list', headers=auth_header(admin_token))
        assert resp.status_code == 200
        assert resp.content_type == 'application/pdf'
