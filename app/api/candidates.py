from flask import request, g
from app.api import api_bp
from app.models.candidate_model import Candidate
from app.schemas.candidates import CreateCandidateSchema, UpdateCandidateSchema, BulkCandidateIdsSchema
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden
from app.services.candidate_service import CandidateService


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/candidates')
def get_candidates():
    query = Candidate.query.filter_by(tenant_id=g.tenant_id, deleted_at=None)

    # Filters
    archived_param = request.args.get('archived', 'false').lower()
    if archived_param != 'all':
        is_archived = archived_param == 'true'
        query = query.filter_by(is_archived=is_archived)

    category_id = request.args.get('category_id')
    if category_id:
        query = query.filter_by(category_id=category_id)

    instructor_id = request.args.get('instructor_id')
    if instructor_id:
        query = query.filter_by(instructor_id=instructor_id)

    search = request.args.get('search')
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db.or_(
                Candidate.first_name.ilike(search_term),
                Candidate.last_name.ilike(search_term),
                Candidate.personal_number.ilike(search_term),
                Candidate.phone.ilike(search_term),
                Candidate.protocol_number.ilike(search_term),
            )
        )

    gender = request.args.get('gender')
    if gender:
        query = query.filter_by(gender=gender)

    date_from = request.args.get('date_from')
    if date_from:
        query = query.filter(Candidate.registration_date >= date_from)

    date_to = request.args.get('date_to')
    if date_to:
        query = query.filter(Candidate.registration_date <= date_to)

    query = query.order_by(Candidate.registration_date.desc())
    result = paginate_query(query)
    result['data'] = [c.to_dict(summary=True) for c in result['data']]
    return result


@api_bp.post('/candidates/bulk-archive')
def bulk_archive_candidates():
    _require_admin()
    payload = parse_body(BulkCandidateIdsSchema, request.get_json(silent=True) or {})
    service = CandidateService()
    count = service.bulk_archive(str(g.tenant_id), payload.candidateIds)
    return {'count': count}


@api_bp.post('/candidates/bulk-unarchive')
def bulk_unarchive_candidates():
    _require_admin()
    payload = parse_body(BulkCandidateIdsSchema, request.get_json(silent=True) or {})
    service = CandidateService()
    count = service.bulk_unarchive(str(g.tenant_id), payload.candidateIds)
    return {'count': count}


@api_bp.get('/candidates/next-protocol-number')
def get_next_protocol_number():
    service = CandidateService()
    protocol_number = service.generate_protocol_number(str(g.tenant_id))
    return {'protocolNumber': protocol_number}


@api_bp.get('/candidates/<candidate_id>')
def get_candidate(candidate_id):
    candidate = Candidate.query.filter_by(
        id=candidate_id, tenant_id=g.tenant_id, deleted_at=None
    ).first()
    if not candidate:
        raise NotFound('Candidate not found')
    return candidate.to_dict()


@api_bp.post('/candidates')
def create_candidate():
    _require_admin()
    payload = parse_body(CreateCandidateSchema, request.get_json(silent=True) or {})
    service = CandidateService()
    candidate = service.create_candidate(str(g.tenant_id), payload.model_dump())
    return candidate.to_dict(), 201


@api_bp.put('/candidates/<candidate_id>')
def update_candidate(candidate_id):
    _require_admin()
    payload = parse_body(UpdateCandidateSchema, request.get_json(silent=True) or {})
    service = CandidateService()
    candidate = service.update_candidate(
        str(g.tenant_id), candidate_id, payload.model_dump(exclude_unset=True)
    )
    return candidate.to_dict()


@api_bp.delete('/candidates/<candidate_id>')
def delete_candidate(candidate_id):
    _require_admin()
    service = CandidateService()
    service.soft_delete(str(g.tenant_id), candidate_id)
    return '', 204


@api_bp.post('/candidates/<candidate_id>/archive')
def archive_candidate(candidate_id):
    _require_admin()
    service = CandidateService()
    candidate = service.archive(str(g.tenant_id), candidate_id)
    return candidate.to_dict()
