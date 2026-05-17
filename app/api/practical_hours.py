from flask import request, g, jsonify
from datetime import datetime, date, time
from app.api import api_bp
from app.models.practical_hour_session_model import PracticalHourSession
from app.models.candidate_model import Candidate
from app.models.instructor_model import Instructor
from app.models.lesson_chapter_model import LessonChapter
from app.schemas.practical_hours import CreatePracticalSessionSchema, UpdatePracticalSessionSchema
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


@api_bp.get('/practical-hours')
def list_practical_sessions():
    """List practical sessions for a candidate."""
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

    query = PracticalHourSession.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    ).order_by(PracticalHourSession.date_realized.desc())

    result = paginate_query(query)
    result['data'] = [s.to_dict() for s in result['data']]
    return result


@api_bp.get('/practical-hours/<session_id>')
def get_practical_session(session_id):
    """Get a specific practical session."""
    session = PracticalHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Practical session not found')

    # Check authorization for instructors
    if g.current_user.get('role') == 'instructor':
        instructor = Instructor.query.filter_by(
            user_id=g.current_user['sub'], tenant_id=g.tenant_id
        ).first()
        if not instructor or str(session.candidate.instructor_id) != str(instructor.id):
            raise Forbidden('Not authorized to view this session')

    return jsonify(session.to_dict())


@api_bp.post('/practical-hours')
def create_practical_session():
    """Create a new practical session and increment candidate practical hours realized."""
    _require_admin()
    payload = parse_body(CreatePracticalSessionSchema, request.get_json(silent=True) or {})

    # Verify candidate exists and belongs to tenant
    candidate = Candidate.query.filter_by(
        id=payload.candidateId, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # Verify instructor if provided
    if payload.instructorId:
        instructor = Instructor.query.filter_by(
            id=payload.instructorId, tenant_id=g.tenant_id
        ).first()
        if not instructor:
            raise NotFound('Instructor not found')

    hours_count = payload.hoursCount or 1
    if hours_count < 1 or hours_count > 200:
        raise ValidationError('hoursCount must be between 1 and 200')

    session = PracticalHourSession(
        candidate_id=payload.candidateId,
        tenant_id=g.tenant_id,
        instructor_id=payload.instructorId,
        date_realized=_parse_date(payload.dateRealized),
        time_realized=_parse_time(payload.timeRealized),
        hours_count=hours_count,
        price_per_hour=payload.pricePerHour or 0.00,
        chapter_topics=payload.chapterTopics,
        remarks=payload.remarks,
        is_paid=payload.isPaid or False,
    )
    db.session.add(session)

    # Increment candidate's practical hours realized
    candidate.practical_hours_realized = (candidate.practical_hours_realized or 0) + (payload.hoursCount or 1)

    db.session.commit()
    return jsonify(session.to_dict()), 201


@api_bp.put('/practical-hours/<session_id>')
def update_practical_session(session_id):
    """Update a practical session and adjust candidate practical hours if needed."""
    _require_admin()
    session = PracticalHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Practical session not found')

    payload = parse_body(UpdatePracticalSessionSchema, request.get_json(silent=True) or {})

    # Handle hours count change
    old_hours = session.hours_count or 0
    if payload.hoursCount is not None:
        if payload.hoursCount < 1 or payload.hoursCount > 200:
            raise ValidationError('hoursCount must be between 1 and 200')
        session.hours_count = payload.hoursCount
        candidate = session.candidate
        hours_diff = (payload.hoursCount or 0) - old_hours
        candidate.practical_hours_realized = max(0, (candidate.practical_hours_realized or 0) + hours_diff)

    if payload.instructorId is not None:
        if payload.instructorId:
            instructor = Instructor.query.filter_by(
                id=payload.instructorId, tenant_id=g.tenant_id
            ).first()
            if not instructor:
                raise NotFound('Instructor not found')
        session.instructor_id = payload.instructorId

    if payload.dateRealized is not None:
        session.date_realized = _parse_date(payload.dateRealized)
    if payload.timeRealized is not None:
        session.time_realized = _parse_time(payload.timeRealized)
    if payload.pricePerHour is not None:
        session.price_per_hour = payload.pricePerHour
    if payload.chapterTopics is not None:
        session.chapter_topics = payload.chapterTopics
    if payload.remarks is not None:
        session.remarks = payload.remarks
    if payload.isPaid is not None:
        session.is_paid = payload.isPaid

    db.session.commit()
    return jsonify(session.to_dict())


@api_bp.delete('/practical-hours/<session_id>')
def delete_practical_session(session_id):
    """Delete a practical session and decrement candidate practical hours realized."""
    _require_admin()
    session = PracticalHourSession.query.filter_by(
        id=session_id, tenant_id=g.tenant_id
    ).first()
    if not session:
        raise NotFound('Practical session not found')

    # Decrement candidate's practical hours realized
    candidate = session.candidate
    hours_to_remove = session.hours_count or 0
    candidate.practical_hours_realized = max(0, (candidate.practical_hours_realized or 0) - hours_to_remove)

    db.session.delete(session)
    db.session.commit()
    return '', 204


@api_bp.post('/practical-hours/generate')
def generate_practical_sessions():
    """Generate practical sessions for a candidate from predefined lesson chapters."""
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
        chapter_type='practical',
        is_active=True,
    ).order_by(LessonChapter.session_number).all()

    if not chapters:
        raise ValidationError('No practical lesson chapters defined for this category')

    today = date.today()
    sessions = []
    for ch in chapters:
        s = PracticalHourSession(
            candidate_id=candidate_id,
            tenant_id=g.tenant_id,
            date_realized=today,
            time_realized=time(9, 0),
            hours_count=ch.hours_count or 1,
            chapter_topics=ch.chapter_topics,
            is_paid=False,
        )
        db.session.add(s)
        sessions.append(s)

    candidate.practical_hours_realized = (candidate.practical_hours_realized or 0) + sum(
        ch.hours_count or 1 for ch in chapters
    )

    db.session.commit()
    return jsonify([s.to_dict() for s in sessions]), 201
