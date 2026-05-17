import json
import pytest
from tests.conftest import auth_header


class TestLessonChaptersCRUD:
    """Tests for lesson chapters CRUD endpoints."""

    def test_create_theory_chapter(self, client, admin_token, category_b):
        res = client.post(
            '/api/v1/lesson-chapters',
            headers=auth_header(admin_token),
            data=json.dumps({
                'categoryId': str(category_b.id),
                'chapterType': 'theory',
                'chapterTopics': '1.1, 1.2, 1.3',
                'timeFrom': '16:00',
                'timeTo': '17:30',
                'hoursCount': 2,
            }),
        )
        assert res.status_code == 201
        body = res.get_json()
        data = body.get('data', body)
        assert data['sessionNumber'] == 1
        assert data['chapterTopics'] == '1.1, 1.2, 1.3'
        assert data['chapterType'] == 'theory'
        assert data['timeFrom'] == '16:00'
        assert data['timeTo'] == '17:30'
        assert data['hoursCount'] == 2
        assert data['isActive'] is True

    def test_create_practical_chapter(self, client, admin_token, category_b):
        res = client.post(
            '/api/v1/lesson-chapters',
            headers=auth_header(admin_token),
            data=json.dumps({
                'categoryId': str(category_b.id),
                'chapterType': 'practical',
                'chapterTopics': '1.1',
                'hoursCount': 2,
            }),
        )
        assert res.status_code == 201
        body = res.get_json()
        data = body.get('data', body)
        assert data['sessionNumber'] == 1
        assert data['chapterTopics'] == '1.1'
        assert data['chapterType'] == 'practical'
        assert data['timeFrom'] is None
        assert data['timeTo'] is None

    def test_auto_increment_session_number(self, client, admin_token, category_b):
        for i, topics in enumerate(['1.1', '2.1', '3.1'], 1):
            res = client.post(
                '/api/v1/lesson-chapters',
                headers=auth_header(admin_token),
                data=json.dumps({
                    'categoryId': str(category_b.id),
                    'chapterType': 'practical',
                    'chapterTopics': topics,
                    'hoursCount': 2,
                }),
            )
            assert res.status_code == 201
            body = res.get_json()
            data = body.get('data', body)
            assert data['sessionNumber'] == i

    def test_list_chapters_filtered(self, client, admin_token, category_b):
        for topics in ['1.1, 1.2', '2.1, 2.2']:
            client.post(
                '/api/v1/lesson-chapters',
                headers=auth_header(admin_token),
                data=json.dumps({
                    'categoryId': str(category_b.id),
                    'chapterType': 'theory',
                    'chapterTopics': topics,
                    'hoursCount': 2,
                }),
            )
        client.post(
            '/api/v1/lesson-chapters',
            headers=auth_header(admin_token),
            data=json.dumps({
                'categoryId': str(category_b.id),
                'chapterType': 'practical',
                'chapterTopics': '1.1',
                'hoursCount': 1,
            }),
        )

        res = client.get(
            f'/api/v1/lesson-chapters?categoryId={category_b.id}&chapterType=theory',
            headers=auth_header(admin_token),
        )
        assert res.status_code == 200
        body = res.get_json()
        data = body.get('data', body)
        assert len(data) == 2
        assert all(ch['chapterType'] == 'theory' for ch in data)

    def test_update_chapter(self, client, admin_token, category_b):
        res = client.post(
            '/api/v1/lesson-chapters',
            headers=auth_header(admin_token),
            data=json.dumps({
                'categoryId': str(category_b.id),
                'chapterType': 'theory',
                'chapterTopics': 'old topics',
                'hoursCount': 2,
            }),
        )
        body = res.get_json()
        chapter_id = body.get('data', body)['id']

        res = client.put(
            f'/api/v1/lesson-chapters/{chapter_id}',
            headers=auth_header(admin_token),
            data=json.dumps({
                'chapterTopics': '1.1, 1.2, 1.3',
                'hoursCount': 3,
            }),
        )
        assert res.status_code == 200
        body = res.get_json()
        data = body.get('data', body)
        assert data['chapterTopics'] == '1.1, 1.2, 1.3'
        assert data['hoursCount'] == 3

    def test_delete_chapter_renumbers(self, client, admin_token, category_b):
        ids = []
        for topics in ['1.1', '2.1', '3.1']:
            res = client.post(
                '/api/v1/lesson-chapters',
                headers=auth_header(admin_token),
                data=json.dumps({
                    'categoryId': str(category_b.id),
                    'chapterType': 'practical',
                    'chapterTopics': topics,
                    'hoursCount': 2,
                }),
            )
            body = res.get_json()
            ids.append(body.get('data', body)['id'])

        res = client.delete(
            f'/api/v1/lesson-chapters/{ids[0]}',
            headers=auth_header(admin_token),
        )
        assert res.status_code == 204

        res = client.get(
            f'/api/v1/lesson-chapters?categoryId={category_b.id}&chapterType=practical',
            headers=auth_header(admin_token),
        )
        body = res.get_json()
        data = body.get('data', body)
        assert len(data) == 2
        assert data[0]['sessionNumber'] == 1
        assert data[0]['chapterTopics'] == '2.1'
        assert data[1]['sessionNumber'] == 2
        assert data[1]['chapterTopics'] == '3.1'

    def test_invalid_chapter_type(self, client, admin_token, category_b):
        res = client.post(
            '/api/v1/lesson-chapters',
            headers=auth_header(admin_token),
            data=json.dumps({
                'categoryId': str(category_b.id),
                'chapterType': 'invalid',
                'chapterTopics': '1.1',
                'hoursCount': 2,
            }),
        )
        assert res.status_code == 400

    def test_instructor_cannot_manage_chapters(self, client, instructor_token, category_b):
        res = client.get(
            '/api/v1/lesson-chapters?chapterType=theory',
            headers=auth_header(instructor_token),
        )
        assert res.status_code == 403


class TestGenerateTheorySessions:
    """Tests for generating theory sessions from lesson chapters."""

    def _create_theory_chapters(self, client, admin_token, category_id):
        chapters = [
            ('1.1, 1.2, 1.3', '16:00', '17:30', 2),
            ('1.4, 1.5, 1.6', '16:00', '17:30', 2),
            ('2.1, 2.2, 2.3', '16:00', '17:30', 2),
        ]
        for topics, t_from, t_to, hours in chapters:
            client.post(
                '/api/v1/lesson-chapters',
                headers=auth_header(admin_token),
                data=json.dumps({
                    'categoryId': str(category_id),
                    'chapterType': 'theory',
                    'chapterTopics': topics,
                    'timeFrom': t_from,
                    'timeTo': t_to,
                    'hoursCount': hours,
                }),
            )

    def test_generate_theory_sessions(self, client, admin_token, candidate, category_b):
        self._create_theory_chapters(client, admin_token, category_b.id)

        res = client.post(
            '/api/v1/theory-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )
        assert res.status_code == 201
        body = res.get_json()
        data = body.get('data', body)
        assert len(data) == 3
        assert data[0]['sessionNumber'] == 1
        assert data[0]['chapterTopics'] == '1.1, 1.2, 1.3'
        assert data[0]['timeFrom'] == '16:00'
        assert data[0]['isRealized'] is False

    def test_generate_fails_if_sessions_exist(self, client, admin_token, candidate, category_b):
        self._create_theory_chapters(client, admin_token, category_b.id)

        client.post(
            '/api/v1/theory-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )

        res = client.post(
            '/api/v1/theory-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )
        assert res.status_code == 400

    def test_generate_fails_without_chapters(self, client, admin_token, candidate):
        res = client.post(
            '/api/v1/theory-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )
        assert res.status_code == 400


class TestGeneratePracticalSessions:
    """Tests for generating practical sessions from lesson chapters."""

    def _create_practical_chapters(self, client, admin_token, category_id):
        chapters = [('1.1', 2), ('2.1', 2), ('3.1', 1)]
        for topics, hours in chapters:
            client.post(
                '/api/v1/lesson-chapters',
                headers=auth_header(admin_token),
                data=json.dumps({
                    'categoryId': str(category_id),
                    'chapterType': 'practical',
                    'chapterTopics': topics,
                    'hoursCount': hours,
                }),
            )

    def test_generate_practical_sessions(self, client, admin_token, candidate, category_b):
        self._create_practical_chapters(client, admin_token, category_b.id)

        res = client.post(
            '/api/v1/practical-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )
        assert res.status_code == 201
        body = res.get_json()
        data = body.get('data', body)
        assert len(data) == 3
        assert data[0]['chapterTopics'] == '1.1'
        assert data[0]['hoursCount'] == 2

    def test_generate_practical_appends_if_sessions_exist(self, client, admin_token, candidate, category_b):
        """Generating sessions twice should append (not reject) per commit 03e207d."""
        self._create_practical_chapters(client, admin_token, category_b.id)

        client.post(
            '/api/v1/practical-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )

        res = client.post(
            '/api/v1/practical-hours/generate',
            headers=auth_header(admin_token),
            data=json.dumps({'candidateId': str(candidate.id)}),
        )
        assert res.status_code == 201


class TestPracticalHoursChapterTopics:
    """Tests for chapter_topics field on practical hour sessions."""

    def test_create_with_chapter_topics(self, client, admin_token, candidate):
        res = client.post(
            '/api/v1/practical-hours',
            headers=auth_header(admin_token),
            data=json.dumps({
                'candidateId': str(candidate.id),
                'dateRealized': '2026-03-10',
                'timeRealized': '10:00',
                'hoursCount': 2,
                'chapterTopics': '1.1',
            }),
        )
        assert res.status_code == 201
        body = res.get_json()
        data = body.get('data', body)
        assert data['chapterTopics'] == '1.1'

    def test_update_chapter_topics(self, client, admin_token, candidate):
        res = client.post(
            '/api/v1/practical-hours',
            headers=auth_header(admin_token),
            data=json.dumps({
                'candidateId': str(candidate.id),
                'dateRealized': '2026-03-10',
                'timeRealized': '10:00',
                'hoursCount': 1,
            }),
        )
        body = res.get_json()
        session_id = body.get('data', body)['id']

        res = client.put(
            f'/api/v1/practical-hours/{session_id}',
            headers=auth_header(admin_token),
            data=json.dumps({'chapterTopics': '2.1'}),
        )
        assert res.status_code == 200
        body = res.get_json()
        data = body.get('data', body)
        assert data['chapterTopics'] == '2.1'
