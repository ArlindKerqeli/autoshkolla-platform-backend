"""Integration tests for payments API endpoints."""
import uuid
import pytest
from tests.conftest import auth_header


class TestListPayments:
    def test_list_payments(self, client, admin_token, candidate):
        resp = client.get(
            f'/api/v1/payments?candidateId={candidate.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    def test_list_payments_missing_candidate_id(self, client, admin_token):
        resp = client.get('/api/v1/payments', headers=auth_header(admin_token))
        assert resp.status_code == 400


class TestCreatePayment:
    def test_create_payment(self, client, admin_token, candidate):
        resp = client.post('/api/v1/payments', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'amount': 100.00,
            'paymentDate': '2026-03-01',
            'paymentMethod': 'cash',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        # Response may be wrapped or direct depending on jsonify usage
        payment = data.get('data', data)
        assert payment['amount'] == 100.00

    def test_create_payment_candidate_not_found(self, client, admin_token):
        resp = client.post('/api/v1/payments', headers=auth_header(admin_token), json={
            'candidateId': str(uuid.uuid4()),
            'amount': 100.00,
            'paymentDate': '2026-03-01',
        })
        assert resp.status_code == 404

    def test_create_payment_instructor_forbidden(self, client, instructor_token, candidate):
        resp = client.post('/api/v1/payments', headers=auth_header(instructor_token), json={
            'candidateId': str(candidate.id),
            'amount': 50.00,
            'paymentDate': '2026-03-01',
        })
        assert resp.status_code == 403


class TestDeletePayment:
    def test_delete_payment(self, client, admin_token, candidate):
        # Create a payment first
        create_resp = client.post('/api/v1/payments', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'amount': 50.00,
            'paymentDate': '2026-03-01',
            'paymentMethod': 'cash',
        })
        data = create_resp.get_json()
        payment = data.get('data', data)
        payment_id = payment['id']
        # Delete it
        resp = client.delete(f'/api/v1/payments/{payment_id}', headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_delete_payment_not_found(self, client, admin_token):
        resp = client.delete(f'/api/v1/payments/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404


class TestPaymentSummary:
    def test_payment_summary(self, client, admin_token, candidate):
        # Create a payment
        client.post('/api/v1/payments', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'amount': 100.00,
            'paymentDate': '2026-03-01',
            'paymentMethod': 'cash',
        })
        resp = client.get('/api/v1/payments/summary', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        summary = data.get('data', data)
        assert summary['totalAmount'] >= 100.00
        assert summary['count'] >= 1
