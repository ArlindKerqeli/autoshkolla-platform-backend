"""Exam tracking API endpoints."""

from flask import request, g, jsonify
from datetime import datetime, date

from app.api import api_bp
from app.models.exam_model import Exam
from app.models.candidate_model import Candidate
from app.schemas.exams import CreateExamSchema, UpdateExamSchema
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden
from app.services.exam_service import exam_service


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


@api_bp.get('/exams')
def list_exams():
    """List exams (paginated, filterable)."""
    query = Exam.query.filter_by(tenant_id=g.tenant_id)

    # Filter by candidate
    candidate_id = request.args.get('candidateId')
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)

    # Filter by exam type
    exam_type = request.args.get('examType')
    if exam_type:
        query = query.filter_by(exam_type=exam_type)

    # Filter by result
    result_filter = request.args.get('result')
    if result_filter:
        query = query.filter_by(result=result_filter)

    # Date range filters
    date_from = request.args.get('dateFrom')
    if date_from:
        parsed = _parse_date(date_from)
        if parsed:
            query = query.filter(Exam.exam_date >= parsed)

    date_to = request.args.get('dateTo')
    if date_to:
        parsed = _parse_date(date_to)
        if parsed:
            query = query.filter(Exam.exam_date <= parsed)

    # Search by candidate name
    search = request.args.get('search')
    if search:
        search_term = f'%{search}%'
        query = query.join(Candidate).filter(
            db.or_(
                Candidate.first_name.ilike(search_term),
                Candidate.last_name.ilike(search_term),
            )
        )

    query = query.order_by(Exam.exam_date.desc())
    result = paginate_query(query)
    result['data'] = [e.to_dict() for e in result['data']]
    return result


@api_bp.get('/candidates/<candidate_id>/exam-eligibility')
def check_exam_eligibility(candidate_id):
    """Check whether a candidate is eligible to take an exam."""
    # Verify candidate belongs to tenant
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')

    eligibility = exam_service.check_eligibility(str(g.tenant_id), candidate_id)
    return eligibility


@api_bp.post('/exams')
def create_exam():
    """Create a new exam record (admin only)."""
    _require_admin()
    payload = parse_body(CreateExamSchema, request.get_json(silent=True) or {})
    exam = exam_service.create_exam(str(g.tenant_id), payload.model_dump())
    return jsonify(exam.to_dict()), 201


@api_bp.put('/exams/<exam_id>')
def update_exam(exam_id):
    """Update an exam record (admin only)."""
    _require_admin()
    payload = parse_body(UpdateExamSchema, request.get_json(silent=True) or {})
    exam = exam_service.update_exam(
        str(g.tenant_id), exam_id, payload.model_dump(exclude_unset=True)
    )
    return jsonify(exam.to_dict())


@api_bp.delete('/exams/<exam_id>')
def delete_exam(exam_id):
    """Delete an exam record (admin only)."""
    _require_admin()
    exam_service.delete_exam(str(g.tenant_id), exam_id)
    return '', 204
