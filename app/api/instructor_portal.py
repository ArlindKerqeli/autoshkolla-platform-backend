from datetime import datetime, date, time as time_type
from flask import request, g
from app.api import api_bp
from app.models.instructor_model import Instructor
from app.models.candidate_model import Candidate
from app.models.instructor_payment_model import InstructorPayment
from app.models.scheduled_lesson_model import ScheduledLesson
from app.models.practical_hour_session_model import PracticalHourSession
from app.models.message_model import Message
from app.schemas.scheduled_lessons import CreatePersonalEventSchema
from app.middleware.error_handler import Forbidden, NotFound, ValidationError
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.utils.db import db
from sqlalchemy import func


def _require_instructor():
    """Verify current user is an instructor and return the instructor record."""
    if g.current_user.get('role') != 'instructor':
        raise Forbidden('Instructor access required')
    user_id = g.current_user['sub']
    instructor = Instructor.query.filter_by(user_id=user_id, tenant_id=g.tenant_id).first()
    if not instructor:
        raise NotFound('Instructor profile not found for this user')
    return instructor


@api_bp.get('/instructor/me')
def instructor_me():
    instructor = _require_instructor()
    data = instructor.to_dict()
    # Add active candidate count
    active_count = Candidate.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id,
        is_archived=False, deleted_at=None
    ).count()
    data['activeCandidatesCount'] = active_count
    # Outstanding debt
    debt_result = InstructorPayment.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    ).with_entities(
        func.coalesce(func.sum(InstructorPayment.amount), 0).label('total'),
        func.coalesce(func.sum(InstructorPayment.amount_paid), 0).label('paid')
    ).first()
    data['outstandingDebt'] = float(debt_result.total) - float(debt_result.paid) if debt_result else 0
    return data


@api_bp.get('/instructor/candidates')
def instructor_candidates():
    instructor = _require_instructor()
    query = Candidate.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id,
        deleted_at=None
    ).order_by(Candidate.registration_date.desc())

    archived = request.args.get('archived', 'false').lower() == 'true'
    query = query.filter_by(is_archived=archived)

    result = paginate_query(query)
    result['data'] = [c.to_dict(summary=True) for c in result['data']]
    return result


@api_bp.get('/instructor/calendar')
def instructor_calendar():
    instructor = _require_instructor()
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    query = ScheduledLesson.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    )
    if date_from:
        query = query.filter(ScheduledLesson.scheduled_date >= date_from)
    if date_to:
        query = query.filter(ScheduledLesson.scheduled_date <= date_to)

    query = query.order_by(ScheduledLesson.scheduled_date, ScheduledLesson.start_time)
    result = paginate_query(query)
    result['data'] = [l.to_dict() for l in result['data']]
    return result


@api_bp.get('/instructor/debt')
def instructor_debt():
    instructor = _require_instructor()

    # Summary
    summary = InstructorPayment.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    ).with_entities(
        func.count().label('total_candidates'),
        func.coalesce(func.sum(InstructorPayment.amount), 0).label('total_owed'),
        func.coalesce(func.sum(InstructorPayment.amount_paid), 0).label('total_paid'),
    ).first()

    total_owed = float(summary.total_owed)
    total_paid = float(summary.total_paid)

    # Per-candidate breakdown
    payments = InstructorPayment.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    ).order_by(InstructorPayment.created_at.desc()).all()

    return {
        'instructorId': str(instructor.id),
        'instructorName': instructor.full_name,
        'totalCandidates': summary.total_candidates,
        'totalAmountOwed': total_owed,
        'totalAmountPaid': total_paid,
        'outstandingBalance': total_owed - total_paid,
        'costPerCandidate': float(instructor.cost_per_candidate) if instructor.cost_per_candidate else 65.00,
        'payments': [p.to_dict() for p in payments],
    }


@api_bp.get('/instructor/dashboard')
def instructor_dashboard():
    instructor = _require_instructor()
    today = date.today()

    # Active candidates count
    active_count = Candidate.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id,
        is_archived=False, deleted_at=None
    ).count()

    # Lessons today
    lessons_today = ScheduledLesson.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id,
        scheduled_date=today, status='scheduled'
    ).count()

    # Outstanding debt
    debt = InstructorPayment.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id
    ).with_entities(
        func.coalesce(func.sum(InstructorPayment.amount), 0).label('total'),
        func.coalesce(func.sum(InstructorPayment.amount_paid), 0).label('paid')
    ).first()

    outstanding = float(debt.total) - float(debt.paid) if debt else 0

    # Unread messages
    user_id = g.current_user['sub']
    unread = Message.query.filter(
        Message.tenant_id == g.tenant_id,
        Message.recipient_id == user_id,
        Message.is_read == False
    ).count()

    # Upcoming lessons today
    upcoming = ScheduledLesson.query.filter_by(
        instructor_id=instructor.id, tenant_id=g.tenant_id,
        scheduled_date=today, status='scheduled'
    ).order_by(ScheduledLesson.start_time).limit(5).all()

    return {
        'activeCandidates': active_count,
        'lessonsToday': lessons_today,
        'outstandingDebt': outstanding,
        'unreadMessages': unread,
        'upcomingLessons': [l.to_dict() for l in upcoming],
    }


def _parse_time(time_str: str) -> time_type:
    """Parse HH:MM string to time object."""
    try:
        parts = time_str.split(':')
        return time_type(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        raise ValidationError(f"Invalid time format: {time_str}. Use HH:MM")


@api_bp.post('/instructor/calendar')
def create_instructor_event():
    """Instructor creates a personal calendar event."""
    instructor = _require_instructor()

    payload = parse_body(CreatePersonalEventSchema, request.get_json(silent=True) or {})

    start_time = _parse_time(payload.startTime)
    end_time = _parse_time(payload.endTime)

    lesson = ScheduledLesson(
        tenant_id=g.tenant_id,
        instructor_id=instructor.id,
        candidate_id=payload.candidateId if payload.candidateId else None,
        title=payload.title,
        scheduled_date=payload.scheduledDate,
        start_time=start_time,
        end_time=end_time,
        notes=payload.notes,
        status='scheduled',
    )
    db.session.add(lesson)
    db.session.commit()
    return lesson.to_dict(), 201


@api_bp.put('/instructor/calendar/<lesson_id>')
def update_instructor_event(lesson_id):
    """Instructor updates their own calendar event."""
    instructor = _require_instructor()

    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id, tenant_id=g.tenant_id, instructor_id=instructor.id
    ).first()
    if not lesson:
        raise NotFound('Event not found')
    if lesson.status != 'scheduled':
        raise ValidationError('Can only edit scheduled events')

    data = request.get_json(silent=True) or {}
    if 'title' in data:
        lesson.title = data['title']
    if 'scheduledDate' in data:
        lesson.scheduled_date = data['scheduledDate']
    if 'startTime' in data:
        lesson.start_time = _parse_time(data['startTime'])
    if 'endTime' in data:
        lesson.end_time = _parse_time(data['endTime'])
    if 'notes' in data:
        lesson.notes = data['notes']
    if 'candidateId' in data:
        lesson.candidate_id = data['candidateId'] if data['candidateId'] else None

    db.session.commit()
    return lesson.to_dict()


@api_bp.put('/instructor/password')
def change_instructor_password():
    """Allow an instructor to change their own password."""
    instructor = _require_instructor()
    data = request.get_json(silent=True) or {}
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not current_password or not new_password:
        raise ValidationError('Fjalekalimi aktual dhe i ri jane te nevojshem')

    from app.models.user_model import User
    user_record = User.query.get(g.current_user['sub'])
    if not user_record or not user_record.check_password(current_password):
        raise ValidationError('Fjalekalimi aktual eshte gabim')

    if len(new_password) < 6:
        raise ValidationError('Fjalekalimi i ri duhet te kete se paku 6 karaktere')

    user_record.set_password(new_password)
    db.session.commit()
    return {'message': 'Fjalekalimi u ndryshua me sukses'}


@api_bp.delete('/instructor/calendar/<lesson_id>')
def delete_instructor_event(lesson_id):
    """Instructor cancels their own calendar event."""
    instructor = _require_instructor()

    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id, tenant_id=g.tenant_id, instructor_id=instructor.id
    ).first()
    if not lesson:
        raise NotFound('Event not found')

    data = request.get_json(silent=True) or {}
    lesson.status = 'cancelled'
    lesson.cancelled_reason = data.get('cancelledReason') or data.get('cancelled_reason')
    db.session.commit()
    return lesson.to_dict()


@api_bp.post('/instructor/calendar/<lesson_id>/complete')
def complete_instructor_lesson(lesson_id):
    """Instructor marks their own lesson as completed."""
    instructor = _require_instructor()

    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id, tenant_id=g.tenant_id, instructor_id=instructor.id
    ).first()
    if not lesson:
        raise NotFound('Lesson not found')
    if lesson.status != 'scheduled':
        raise ValidationError('Can only complete scheduled lessons')

    lesson.status = 'completed'

    # Auto-create practical hour session for candidate lessons
    if lesson.candidate_id:
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
        db.session.flush()
        lesson.practical_session_id = session.id

    db.session.commit()
    return lesson.to_dict()


@api_bp.post('/instructor/calendar/<lesson_id>/no-show')
def mark_instructor_lesson_no_show(lesson_id):
    """Instructor marks a lesson as no-show."""
    instructor = _require_instructor()

    lesson = ScheduledLesson.query.filter_by(
        id=lesson_id, tenant_id=g.tenant_id, instructor_id=instructor.id
    ).first()
    if not lesson:
        raise NotFound('Lesson not found')
    if lesson.status != 'scheduled':
        raise ValidationError('Can only mark scheduled lessons as no-show')
    lesson.status = 'no_show'
    db.session.commit()
    return lesson.to_dict()
