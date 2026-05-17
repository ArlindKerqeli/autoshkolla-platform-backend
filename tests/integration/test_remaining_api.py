"""Integration tests for theory hours, practical hours, expenses, locations, and other API endpoints."""
import uuid
import pytest
from app.utils.db import db as _db
from app.models.theory_hour_session_model import TheoryHourSession
from app.models.practical_hour_session_model import PracticalHourSession
from app.models.expense_type_model import ExpenseType
from app.models.expense_model import Expense
from app.models.instructor_payment_model import InstructorPayment
from tests.conftest import auth_header


# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------
class TestLocations:
    def test_get_countries(self, client, admin_token):
        resp = client.get('/api/v1/locations/countries', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_get_municipalities(self, client, admin_token):
        resp = client.get('/api/v1/locations/municipalities', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_get_places(self, client, admin_token):
        resp = client.get('/api/v1/locations/places', headers=auth_header(admin_token))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Theory Hours
# ---------------------------------------------------------------------------
class TestTheoryHours:
    def test_list_theory_sessions(self, client, admin_token, candidate):
        resp = client.get(
            f'/api/v1/theory-hours?candidateId={candidate.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_list_theory_sessions_missing_candidate(self, client, admin_token):
        resp = client.get('/api/v1/theory-hours', headers=auth_header(admin_token))
        assert resp.status_code == 400

    def test_create_theory_session(self, client, admin_token, candidate):
        resp = client.post('/api/v1/theory-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 1,
            'chapterTopics': 'Rregullat e trafikut',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        session = data.get('data', data)
        assert session['sessionNumber'] == 1

    def test_create_theory_duplicate_session(self, client, admin_token, candidate):
        client.post('/api/v1/theory-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 1,
            'chapterTopics': 'Rregullat e trafikut',
        })
        resp = client.post('/api/v1/theory-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 1,
            'chapterTopics': 'Duplicate',
        })
        assert resp.status_code == 400

    def test_update_theory_session(self, client, admin_token, candidate):
        create_resp = client.post('/api/v1/theory-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 2,
            'chapterTopics': 'Original',
        })
        session = create_resp.get_json().get('data', create_resp.get_json())
        resp = client.put(
            f'/api/v1/theory-hours/{session["id"]}',
            headers=auth_header(admin_token),
            json={'chapterTopics': 'Updated topic'},
        )
        assert resp.status_code == 200

    def test_delete_theory_session(self, client, admin_token, candidate):
        create_resp = client.post('/api/v1/theory-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 3,
            'chapterTopics': 'Delete me',
        })
        session = create_resp.get_json().get('data', create_resp.get_json())
        resp = client.delete(f'/api/v1/theory-hours/{session["id"]}', headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_realize_theory_session(self, client, admin_token, candidate):
        create_resp = client.post('/api/v1/theory-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 4,
            'chapterTopics': 'To realize',
        })
        session = create_resp.get_json().get('data', create_resp.get_json())
        resp = client.post(f'/api/v1/theory-hours/{session["id"]}/realize', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json().get('data', resp.get_json())
        assert data['isRealized'] is True

    def test_theory_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/theory-hours/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_theory_instructor_forbidden(self, client, instructor_token, candidate):
        resp = client.post('/api/v1/theory-hours', headers=auth_header(instructor_token), json={
            'candidateId': str(candidate.id),
            'sessionNumber': 1,
            'chapterTopics': 'Test',
        })
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Practical Hours
# ---------------------------------------------------------------------------
class TestPracticalHours:
    def test_list_practical_sessions(self, client, admin_token, candidate):
        resp = client.get(
            f'/api/v1/practical-hours?candidateId={candidate.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_list_practical_sessions_missing_candidate(self, client, admin_token):
        resp = client.get('/api/v1/practical-hours', headers=auth_header(admin_token))
        assert resp.status_code == 400

    def test_create_practical_session(self, client, admin_token, candidate, instructor):
        resp = client.post('/api/v1/practical-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'instructorId': str(instructor.id),
            'dateRealized': '2026-03-01',
            'timeRealized': '10:00',
            'hoursCount': 2,
            'pricePerHour': 10.00,
        })
        assert resp.status_code == 201

    def test_create_practical_session_candidate_not_found(self, client, admin_token):
        resp = client.post('/api/v1/practical-hours', headers=auth_header(admin_token), json={
            'candidateId': str(uuid.uuid4()),
            'dateRealized': '2026-03-01',
            'timeRealized': '10:00',
        })
        assert resp.status_code == 404

    def test_update_practical_session(self, client, admin_token, candidate, instructor):
        create_resp = client.post('/api/v1/practical-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'instructorId': str(instructor.id),
            'dateRealized': '2026-03-01',
            'timeRealized': '10:00',
            'hoursCount': 1,
        })
        session = create_resp.get_json()
        session_id = session.get('id') or session.get('data', {}).get('id')
        resp = client.put(
            f'/api/v1/practical-hours/{session_id}',
            headers=auth_header(admin_token),
            json={'hoursCount': 3, 'remarks': 'Updated'},
        )
        assert resp.status_code == 200

    def test_delete_practical_session(self, client, admin_token, candidate, instructor):
        create_resp = client.post('/api/v1/practical-hours', headers=auth_header(admin_token), json={
            'candidateId': str(candidate.id),
            'instructorId': str(instructor.id),
            'dateRealized': '2026-03-01',
            'timeRealized': '10:00',
            'hoursCount': 2,
        })
        session = create_resp.get_json()
        session_id = session.get('id') or session.get('data', {}).get('id')
        resp = client.delete(f'/api/v1/practical-hours/{session_id}', headers=auth_header(admin_token))
        assert resp.status_code == 204

    def test_practical_session_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/practical-hours/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_practical_instructor_forbidden(self, client, instructor_token, candidate):
        resp = client.post('/api/v1/practical-hours', headers=auth_header(instructor_token), json={
            'candidateId': str(candidate.id),
            'dateRealized': '2026-03-01',
            'timeRealized': '10:00',
        })
        assert resp.status_code == 403

    def test_update_practical_not_found(self, client, admin_token):
        resp = client.put(
            f'/api/v1/practical-hours/{uuid.uuid4()}',
            headers=auth_header(admin_token),
            json={'hoursCount': 3},
        )
        assert resp.status_code == 404

    def test_delete_practical_not_found(self, client, admin_token):
        resp = client.delete(f'/api/v1/practical-hours/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Expenses
# ---------------------------------------------------------------------------
class TestExpenses:
    @pytest.fixture
    def expense_type(self, tenant_a):
        et = ExpenseType(
            tenant_id=tenant_a.id,
            name='Karburant',
            is_active=True,
        )
        _db.session.add(et)
        _db.session.commit()
        return et

    def test_list_expense_types(self, client, admin_token):
        resp = client.get('/api/v1/expense-types', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_create_expense_type(self, client, admin_token):
        resp = client.post('/api/v1/expense-types', headers=auth_header(admin_token), json={
            'name': 'Mirëmbajtje',
        })
        assert resp.status_code == 201

    def test_list_expenses(self, client, admin_token):
        resp = client.get('/api/v1/expenses', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_create_expense(self, client, admin_token, expense_type, vehicle):
        resp = client.post('/api/v1/expenses', headers=auth_header(admin_token), json={
            'expenseTypeId': str(expense_type.id),
            'vehicleId': str(vehicle.id),
            'amount': 50.00,
            'date': '2026-03-01',
            'description': 'Karburant i ditës',
        })
        assert resp.status_code == 201

    def test_expenses_summary(self, client, admin_token):
        resp = client.get('/api/v1/expenses-summary', headers=auth_header(admin_token))
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Instructor Payments (correct route pattern)
# ---------------------------------------------------------------------------
class TestInstructorPayments:
    def test_debt_summaries(self, client, admin_token, instructor):
        resp = client.get('/api/v1/instructors/debt-summaries', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert isinstance(result, list)

    def test_instructor_debt_summary(self, client, admin_token, instructor):
        resp = client.get(
            f'/api/v1/instructors/{instructor.id}/debt-summary',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert result['instructorId'] == str(instructor.id)

    def test_instructor_debt_summary_not_found(self, client, admin_token):
        resp = client.get(
            f'/api/v1/instructors/{uuid.uuid4()}/debt-summary',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_instructor_payments_list(self, client, admin_token, instructor):
        resp = client.get(
            f'/api/v1/instructors/{instructor.id}/payments',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_record_instructor_payment(self, client, admin_token, candidate, instructor):
        ip = InstructorPayment(
            tenant_id=candidate.tenant_id,
            instructor_id=instructor.id,
            candidate_id=candidate.id,
            amount=65.00,
            amount_paid=0,
            status='pending',
        )
        _db.session.add(ip)
        _db.session.commit()

        resp = client.post(
            f'/api/v1/instructors/{instructor.id}/payments',
            headers=auth_header(admin_token),
            json={
                'candidateId': str(candidate.id),
                'amount': 30.00,
                'paymentMethod': 'cash',
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        result = data.get('data', data)
        assert float(result['amountPaid']) == 30.00
        assert result['status'] == 'partial'

    def test_record_instructor_payment_full(self, client, admin_token, candidate, instructor):
        ip = InstructorPayment(
            tenant_id=candidate.tenant_id,
            instructor_id=instructor.id,
            candidate_id=candidate.id,
            amount=65.00,
            amount_paid=0,
            status='pending',
        )
        _db.session.add(ip)
        _db.session.commit()

        resp = client.post(
            f'/api/v1/instructors/{instructor.id}/payments',
            headers=auth_header(admin_token),
            json={
                'candidateId': str(candidate.id),
                'amount': 65.00,
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        result = data.get('data', data)
        assert result['status'] == 'paid'

    def test_record_instructor_payment_missing_fields(self, client, admin_token, instructor):
        resp = client.post(
            f'/api/v1/instructors/{instructor.id}/payments',
            headers=auth_header(admin_token),
            json={},
        )
        assert resp.status_code == 400

    def test_record_instructor_payment_no_record(self, client, admin_token, instructor, candidate):
        resp = client.post(
            f'/api/v1/instructors/{instructor.id}/payments',
            headers=auth_header(admin_token),
            json={
                'candidateId': str(candidate.id),
                'amount': 30.00,
            },
        )
        assert resp.status_code == 404

    def test_debt_summaries_forbidden_instructor(self, client, instructor_token):
        resp = client.get('/api/v1/instructors/debt-summaries', headers=auth_header(instructor_token))
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Users - additional tests
# ---------------------------------------------------------------------------
class TestUsersAdditional:
    def test_get_user(self, client, admin_token, admin_user):
        resp = client.get(f'/api/v1/users/{admin_user.id}', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_get_user_not_found(self, client, admin_token):
        resp = client.get(f'/api/v1/users/{uuid.uuid4()}', headers=auth_header(admin_token))
        assert resp.status_code == 404

    def test_list_users_filter_role(self, client, admin_token, admin_user):
        resp = client.get('/api/v1/users?role=administrator', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert all(u['role'] == 'administrator' for u in data['data'])

    def test_list_users_search(self, client, admin_token, admin_user):
        resp = client.get('/api/v1/users?search=Admin', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_change_password(self, client, admin_token, admin_user):
        resp = client.put(
            f'/api/v1/users/{admin_user.id}/password',
            headers=auth_header(admin_token),
            json={'password': 'NewPass456!'},
        )
        assert resp.status_code == 200

    def test_delete_user(self, client, admin_token, instructor_user):
        resp = client.delete(
            f'/api/v1/users/{instructor_user.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 204

    def test_delete_user_cannot_delete_self(self, client, admin_token, admin_user):
        resp = client.delete(
            f'/api/v1/users/{admin_user.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 400

    def test_delete_user_not_found(self, client, admin_token):
        resp = client.delete(
            f'/api/v1/users/{uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_list_users_filter_active(self, client, admin_token, admin_user):
        resp = client.get('/api/v1/users?isActive=true', headers=auth_header(admin_token))
        assert resp.status_code == 200
