from flask import request, g, jsonify
from datetime import datetime, date
from app.api import api_bp
from app.models.verification_model import Verification
from app.models.candidate_model import Candidate
from app.models.category_model import Category
from app.models.instructor_model import Instructor
from app.schemas.verifications import CreateVerificationSchema, UpdateVerificationSchema
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden


def _require_admin():
    """Require administrator role."""
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


def _parse_date(date_str: str) -> date:
    """Parse date string (YYYY-MM-DD format) to date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(f'Invalid date format: {date_str}')


@api_bp.get('/verifications')
def list_verifications():
    """List verifications for a candidate."""
    candidate_id = request.args.get('candidateId')
    if not candidate_id:
        raise ValidationError('candidateId is required')

    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    query = Verification.query.filter_by(
        candidate_id=candidate_id, tenant_id=g.tenant_id
    ).order_by(Verification.verification_date.desc())

    result = paginate_query(query)
    result['data'] = [v.to_dict() for v in result['data']]
    return result


@api_bp.get('/verifications/<verification_id>')
def get_verification(verification_id):
    """Get a specific verification."""
    verification = Verification.query.filter_by(
        id=verification_id, tenant_id=g.tenant_id
    ).first()
    if not verification:
        raise NotFound('Verification not found')

    return jsonify(verification.to_dict())


@api_bp.post('/verifications')
def create_verification():
    """Create a new verification."""
    _require_admin()
    payload = parse_body(CreateVerificationSchema, request.get_json(silent=True) or {})

    # Verify candidate exists and belongs to tenant
    candidate = Candidate.query.filter_by(
        id=payload.candidateId, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    # Verify category exists
    category = Category.query.filter_by(
        id=payload.categoryId, tenant_id=g.tenant_id
    ).first()
    if not category:
        raise NotFound('Category not found')

    # Verify lecturer if provided
    if payload.lecturerId:
        lecturer = Instructor.query.filter_by(
            id=payload.lecturerId, tenant_id=g.tenant_id
        ).first()
        if not lecturer:
            raise NotFound('Lecturer not found')

    # Verify instructor if provided
    if payload.instructorId:
        instructor = Instructor.query.filter_by(
            id=payload.instructorId, tenant_id=g.tenant_id
        ).first()
        if not instructor:
            raise NotFound('Instructor not found')

    verification = Verification(
        candidate_id=payload.candidateId,
        tenant_id=g.tenant_id,
        category_id=payload.categoryId,
        verification_date=_parse_date(payload.verificationDate),
        theory_hours_start=_parse_date(payload.theoryHoursStart),
        theory_hours_end=_parse_date(payload.theoryHoursEnd),
        practical_hours_start=_parse_date(payload.practicalHoursStart),
        practical_hours_end=_parse_date(payload.practicalHoursEnd),
        sequence_number=payload.sequenceNumber,
        lecturer_id=payload.lecturerId,
        instructor_id=payload.instructorId,
        red_cross_cert=payload.redCrossCert or False,
        id_card_copy=payload.idCardCopy or False,
    )
    db.session.add(verification)
    db.session.commit()

    return jsonify(verification.to_dict()), 201


@api_bp.put('/verifications/<verification_id>')
def update_verification(verification_id):
    """Update a verification."""
    _require_admin()
    verification = Verification.query.filter_by(
        id=verification_id, tenant_id=g.tenant_id
    ).first()
    if not verification:
        raise NotFound('Verification not found')

    payload = parse_body(UpdateVerificationSchema, request.get_json(silent=True) or {})

    # Verify lecturer if provided
    if payload.lecturerId is not None and payload.lecturerId:
        lecturer = Instructor.query.filter_by(
            id=payload.lecturerId, tenant_id=g.tenant_id
        ).first()
        if not lecturer:
            raise NotFound('Lecturer not found')

    # Verify instructor if provided
    if payload.instructorId is not None and payload.instructorId:
        instructor = Instructor.query.filter_by(
            id=payload.instructorId, tenant_id=g.tenant_id
        ).first()
        if not instructor:
            raise NotFound('Instructor not found')

    if payload.verificationDate is not None:
        verification.verification_date = _parse_date(payload.verificationDate)
    if payload.theoryHoursStart is not None:
        verification.theory_hours_start = _parse_date(payload.theoryHoursStart)
    if payload.theoryHoursEnd is not None:
        verification.theory_hours_end = _parse_date(payload.theoryHoursEnd)
    if payload.practicalHoursStart is not None:
        verification.practical_hours_start = _parse_date(payload.practicalHoursStart)
    if payload.practicalHoursEnd is not None:
        verification.practical_hours_end = _parse_date(payload.practicalHoursEnd)
    if payload.sequenceNumber is not None:
        verification.sequence_number = payload.sequenceNumber
    if payload.lecturerId is not None:
        verification.lecturer_id = payload.lecturerId
    if payload.instructorId is not None:
        verification.instructor_id = payload.instructorId
    if payload.redCrossCert is not None:
        verification.red_cross_cert = payload.redCrossCert
    if payload.idCardCopy is not None:
        verification.id_card_copy = payload.idCardCopy

    db.session.commit()
    return jsonify(verification.to_dict())


@api_bp.delete('/verifications/<verification_id>')
def delete_verification(verification_id):
    """Delete a verification."""
    _require_admin()
    verification = Verification.query.filter_by(
        id=verification_id, tenant_id=g.tenant_id
    ).first()
    if not verification:
        raise NotFound('Verification not found')

    db.session.delete(verification)
    db.session.commit()
    return '', 204
