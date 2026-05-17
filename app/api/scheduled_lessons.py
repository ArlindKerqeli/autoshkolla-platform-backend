from datetime import datetime, time
from flask import request, g
from app.api import api_bp
from app.models.scheduled_lesson_model import ScheduledLesson
from app.models.practical_hour_session_model import PracticalHourSession
from app.schemas.scheduled_lessons import CreateScheduledLessonSchema, UpdateScheduledLessonSchema
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.middleware.error_handler import NotFound, Forbidden, ValidationError
from app.utils.db import db


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


def _parse_time(time_str: str) -> time:
    """Parse HH:MM string to time object."""
    try:
        parts = time_str.split(':')
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        raise ValidationError(f"Invalid time format: {time_str}. Use HH:MM")


def _create_practical_session(lesson: ScheduledLesson) -> PracticalHourSession:
    """Create a PracticalHourSession from a completed scheduled lesson."""
    # Calculate hours from time difference
    start_minutes = lesson.start_time.hour * 60 + lesson.start_time.minute
    end_minutes = lesson.end_time.hour * 60 + lesson.end_time.minute
    duration_hours = max(1, round((end_minutes - start_minutes) / 60))

    session = PracticalHourSession(
        tenant_id=lesson.tenant_id,
        candidate_id=lesson.candidate_id,
        instructor_id=lesson.instructor_id,
        date_realized=lesson.scheduled_date,
        time_realized=lesson.start_time,
        hours_count=duration_hours,
        remarks=lesson.notes,
    )
    db.session.add(session)
    db.session.flush()  # Get session.id before commit
    lesson.practical_session_id = session.id
    return session


@api_bp.get('/scheduled-lessons')
def get_scheduled_lessons():
    query = ScheduledLesson.query.filter_by(tenant_id=g.tenant_id)

    instructor_id = request.args.get('instructor_id')
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)

    candidate_id = request.args.get('candidate_id')
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(ScheduledLesson.scheduled_date >= date_from)

    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(ScheduledLesson.scheduled_date <= date_to)

    query = query.order_by(ScheduledLesson.scheduled_date, ScheduledLesson.start_time)
    result = paginate_query(query)
    result['data'] = [l.to_dict() for l in result['data']]
    return result


@api_bp.post('/scheduled-lessons')
def create_scheduled_lesson():
    _require_admin()
    payload = parse_body(CreateScheduledLessonSchema, request.get_json(silent=True) or {})
    lesson = ScheduledLesson(
        tenant_id=g.tenant_id,
        instructor_id=payload.instructorId,
        candidate_id=payload.candidateId if payload.candidateId else None,
        vehicle_id=payload.vehicleId,
        scheduled_date=payload.scheduledDate,
        start_time=_parse_time(payload.startTime),
        end_time=_parse_time(payload.endTime),
        title=payload.title,
        notes=payload.notes,
    )
    db.session.add(lesson)
    db.session.commit()
    return lesson.to_dict(), 201


@api_bp.put('/scheduled-lessons/<lesson_id>')
def update_scheduled_lesson(lesson_id):
    _require_admin()
    lesson = ScheduledLesson.query.filter_by(id=lesson_id, tenant_id=g.tenant_id).first()
    if not lesson:
        raise NotFound('Scheduled lesson not found')
    if lesson.status != 'scheduled':
        raise ValidationError('Can only update scheduled lessons')

    payload = parse_body(UpdateScheduledLessonSchema, request.get_json(silent=True) or {})
    data = payload.model_dump(exclude_none=True)

    if 'candidateId' in data:
        lesson.candidate_id = data['candidateId'] if data['candidateId'] else None
    if 'vehicleId' in data:
        lesson.vehicle_id = data['vehicleId']
    if 'scheduledDate' in data:
        lesson.scheduled_date = data['scheduledDate']
    if 'startTime' in data:
        lesson.start_time = _parse_time(data['startTime'])
    if 'endTime' in data:
        lesson.end_time = _parse_time(data['endTime'])
    if 'title' in data:
        lesson.title = data['title']
    if 'notes' in data:
        lesson.notes = data['notes']

    db.session.commit()
    return lesson.to_dict()


@api_bp.delete('/scheduled-lessons/<lesson_id>')
def cancel_scheduled_lesson(lesson_id):
    _require_admin()
    lesson = ScheduledLesson.query.filter_by(id=lesson_id, tenant_id=g.tenant_id).first()
    if not lesson:
        raise NotFound('Scheduled lesson not found')

    data = request.get_json(silent=True) or {}
    lesson.status = 'cancelled'
    lesson.cancelled_reason = data.get('cancelledReason', data.get('cancelled_reason'))
    db.session.commit()
    return lesson.to_dict()


@api_bp.post('/scheduled-lessons/<lesson_id>/complete')
def complete_scheduled_lesson(lesson_id):
    _require_admin()
    lesson = ScheduledLesson.query.filter_by(id=lesson_id, tenant_id=g.tenant_id).first()
    if not lesson:
        raise NotFound('Scheduled lesson not found')
    if lesson.status != 'scheduled':
        raise ValidationError('Can only complete scheduled lessons')

    lesson.status = 'completed'

    # Auto-create practical hour session for candidate lessons
    if lesson.candidate_id:
        _create_practical_session(lesson)

    db.session.commit()
    return lesson.to_dict()


@api_bp.post('/scheduled-lessons/<lesson_id>/no-show')
def mark_lesson_no_show(lesson_id):
    """Mark a scheduled lesson as no-show."""
    _require_admin()
    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id, tenant_id=g.tenant_id
    ).first()
    if not lesson:
        raise NotFound('Scheduled lesson not found')
    if lesson.status != 'scheduled':
        raise ValidationError('Can only mark scheduled lessons as no-show')
    lesson.status = 'no_show'
    db.session.commit()
    return lesson.to_dict()
