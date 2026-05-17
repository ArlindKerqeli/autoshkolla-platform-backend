from flask import request, g, jsonify
from datetime import datetime, date, time
from app.api import api_bp
from app.models.theory_hour_session_model import TheoryHourSession
from app.models.candidate_model import Candidate
from app.models.instructor_model import Instructor
from app.models.lesson_chapter_model import LessonChapter
from app.schemas.theory_hours import CreateTheorySessionSchema, UpdateTheorySessionSchema
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden


def _require_admin():
    """Require administrator role."""
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


def _parse_time(time_str: str) -> time:
    """Parse time string (HH:MM format) to time object."""
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        raise ValidationError(f'Invalid time format: {time_str}')


def _parse_date(date_str: str) -> date:
    """Parse date string (YYYY-MM-DD format) to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(f'Invalid date format: {date_str}')


@api_bp.get('/theory-hours')
def list_theory_sessions():
    """List theory sessions for a candidate."""
    candidate_id = request.args.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # If instructor role, verify candidate is assigned to them
    if g.current_user.get('role') == 'instructor':
        instructor = Instructor.query.filter_by(
            user_id=g.current_user['sub'], tenant_id=g.tenant_id
        ).first()
        if not instructor or str(candidate.instructor_id) != str(instructor.id):
            raise Forbidden('Not authorized to view this candidate')

    query = TheoryHourSession.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    ).order_by(TheoryHourSession.session_number)

    result = paginate_query(query)
    result['data'] = [s.to_dict() for s in result['data']]
    return result


@api_bp.get('/theory-hours/<session_id>')
def get_theory_session(session_id):
    """Get a specific theory session."""
    session = TheoryHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Theory session not found')

    # Check authorization for instructors
    if g.current_user.get('role') == 'instructor':
        instructor = Instructor.query.filter_by(
            user_id=g.current_user['sub'], tenant_id=g.tenant_id
        ).first()
        if not instructor or str(session.candidate.instructor_id) != str(instructor.id):
            raise Forbidden('Not authorized to view this session')

    return jsonify(session.to_dict())


@api_bp.post('/theory-hours')
def create_theory_session():
    """Create a new theory session."""
    _require_admin()
    payload = parse_body(CreateTheorySessionSchema, request.get_json(silent=True) or {})

    # Verify candidate exists and belongs to tenant
    candidate = Candidate.query.filter_by(
        id=payload.candidateId, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # Check if session number already exists for this candidate
    existing = TheoryHourSession.query.filter_by(
        candidate_id=payload.candidateId,
        session_number=payload.sessionNumber,
        tenant_id=g.tenant_id
    ).first()
    if existing:
        raise ValidationError(f'Session number {payload.sessionNumber} already exists for this candidate')

    session = TheoryHourSession(
        candidate_id=payload.candidateId,
        tenant_id=g.tenant_id,
        session_number=payload.sessionNumber,
        chapter_topics=payload.chapterTopics,
        date_realized=_parse_date(payload.dateRealized) if payload.dateRealized else None,
        time_from=_parse_time(payload.timeFrom) if payload.timeFrom else time(16, 0),
        time_to=_parse_time(payload.timeTo) if payload.timeTo else time(17, 30),
        hours_count=payload.hoursCount or 2,
        is_realized=payload.isRealized or False,
    )
    db.session.add(session)
    db.session.commit()

    return jsonify(session.to_dict()), 201


@api_bp.put('/theory-hours/<session_id>')
def update_theory_session(session_id):
    """Update a theory session."""
    _require_admin()
    session = TheoryHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Theory session not found')

    payload = parse_body(UpdateTheorySessionSchema, request.get_json(silent=True) or {})

    if payload.chapterTopics is not None:
        session.chapter_topics = payload.chapterTopics
    if payload.dateRealized is not None:
        session.date_realized = _parse_date(payload.dateRealized)
    if payload.timeFrom is not None:
        session.time_from = _parse_time(payload.timeFrom)
    if payload.timeTo is not None:
        session.time_to = _parse_time(payload.timeTo)
    if payload.hoursCount is not None:
        session.hours_count = payload.hoursCount
    if payload.isRealized is not None:
        session.is_realized = payload.isRealized

    db.session.commit()
    return jsonify(session.to_dict())


@api_bp.delete('/theory-hours/<session_id>')
def delete_theory_session(session_id):
    """Delete a theory session."""
    _require_admin()
    session = TheoryHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Theory session not found')

    db.session.delete(session)
    db.session.commit()
    return '', 204


@api_bp.post('/theory-hours/<session_id>/realize')
def realize_theory_session(session_id):
    """Mark a theory session as realized."""
    _require_admin()
    session = TheoryHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Theory session not found')

    session.is_realized = True
    if not session.date_realized:
        session.date_realized = date.today()

    db.session.commit()
    return jsonify(session.to_dict())


@api_bp.post('/theory-hours/generate')
def generate_theory_sessions():
    """Generate theory sessions for a candidate from predefined lesson chapters."""
    _require_admin()
    payload = request.get_json(silent=True) or {}
    candidate_id = payload.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    if not candidate.category_id:
        raise ValidationError('Candidate has no category assigned')

    chapters = LessonChapter.query.filter_by(
        tenant_id=g.tenant_id,
        category_id=candidate.category_id,
        chapter_type='theory',
        is_active=True,
    ).order_by(LessonChapter.session_number).all()

    if not chapters:
        raise ValidationError('No theory lesson chapters defined for this category')

    # Get existing session chapter_topics for this candidate to allow appending
    existing_sessions = TheoryHourSession.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    ).all()
    existing_topics = {s.chapter_topics for s in existing_sessions}

    # Find the highest existing session_number to continue numbering from there
    max_session_number = max((s.session_number for s in existing_sessions), default=0)

    # Only create sessions for chapters not already present
    new_sessions = []
    next_number = max_session_number + 1
    for ch in chapters:
        if ch.chapter_topics not in existing_topics:
            s = TheoryHourSession(
                candidate_id=candidate_id,
                tenant_id=g.tenant_id,
                session_number=next_number,
                chapter_topics=ch.chapter_topics,
                time_from=ch.time_from or time(16, 0),
                time_to=ch.time_to or time(17, 30),
                hours_count=ch.hours_count or 2,
                is_realized=False,
            )
            db.session.add(s)
            new_sessions.append(s)
            next_number += 1

    if not new_sessions:
        raise ValidationError('Nuk ka kapituj te rinj per te gjeneruar — te gjitha sesionet ekzistojne')

    db.session.commit()
    return jsonify([s.to_dict() for s in new_sessions]), 201
