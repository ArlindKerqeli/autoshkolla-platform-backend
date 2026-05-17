"""Integration tests for scheduled lessons API endpoints."""
import uuid
import pytest
from app.utils.db import db as _db
from app.models.scheduled_lesson_model import ScheduledLesson
from tests.conftest import auth_header


class TestScheduledLessons:
    def test_list_scheduled_lessons(self, client, admin_token):
        resp = client.get('/api/v1/scheduled-lessons', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_create_scheduled_lesson(self, client, admin_token, candidate, instructor, vehicle):
        resp = client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'vehicleId': str(vehicle.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
            'notes': 'Mësim praktik',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        result = data.get('data', data)
        assert result['status'] == 'scheduled'

    def test_list_filter_by_instructor(self, client, admin_token, candidate, instructor, vehicle):
        # Create a lesson first
        client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
        })
        resp = client.get(
            f'/api/v1/scheduled-lessons?instructor_id={instructor.id}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_list_filter_by_date_range(self, client, admin_token, candidate, instructor):
        client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
        })
        resp = client.get(
            '/api/v1/scheduled-lessons?date_from=2026-03-01&date_to=2026-03-31',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_update_scheduled_lesson(self, client, admin_token, candidate, instructor):
        create_resp = client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
        })
        lesson = create_resp.get_json()
        lesson_id = lesson.get('id') or lesson.get('data', {}).get('id')
        resp = client.put(
            f'/api/v1/scheduled-lessons/{lesson_id}',
            headers=auth_header(admin_token),
            json={'notes': 'Updated notes', 'startTime': '11:00', 'endTime': '12:00'},
        )
        assert resp.status_code == 200

    def test_update_not_found(self, client, admin_token):
        resp = client.put(
            f'/api/v1/scheduled-lessons/{uuid.uuid4()}',
            headers=auth_header(admin_token),
            json={'notes': 'X'},
        )
        assert resp.status_code == 404

    def test_cancel_scheduled_lesson(self, client, admin_token, candidate, instructor):
        create_resp = client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
        })
        lesson = create_resp.get_json()
        lesson_id = lesson.get('id') or lesson.get('data', {}).get('id')
        resp = client.delete(
            f'/api/v1/scheduled-lessons/{lesson_id}',
            headers=auth_header(admin_token),
            json={'cancelledReason': 'Kandidati nuk ka ardhur'},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert result['status'] == 'cancelled'

    def test_cancel_not_found(self, client, admin_token):
        resp = client.delete(
            f'/api/v1/scheduled-lessons/{uuid.uuid4()}',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_complete_scheduled_lesson(self, client, admin_token, candidate, instructor):
        create_resp = client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
        })
        lesson = create_resp.get_json()
        lesson_id = lesson.get('id') or lesson.get('data', {}).get('id')
        resp = client.post(
            f'/api/v1/scheduled-lessons/{lesson_id}/complete',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert result['status'] == 'completed'

    def test_complete_not_found(self, client, admin_token):
        resp = client.post(
            f'/api/v1/scheduled-lessons/{uuid.uuid4()}/complete',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_complete_already_cancelled(self, client, admin_token, candidate, instructor):
        create_resp = client.post('/api/v1/scheduled-lessons', headers=auth_header(admin_token), json={
            'instructorId': str(instructor.id),
            'candidateId': str(candidate.id),
            'scheduledDate': '2026-03-15',
            'startTime': '10:00',
            'endTime': '11:00',
        })
        lesson = create_resp.get_json()
        lesson_id = lesson.get('id') or lesson.get('data', {}).get('id')
        # Cancel first
        client.delete(f'/api/v1/scheduled-lessons/{lesson_id}', headers=auth_header(admin_token))
        # Then try to complete
        resp = client.post(
            f'/api/v1/scheduled-lessons/{lesson_id}/complete',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 400
