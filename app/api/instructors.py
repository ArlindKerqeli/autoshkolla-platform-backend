from flask import request, g
from app.api import api_bp
from app.models.instructor_model import Instructor
from app.schemas.instructors import CreateInstructorSchema, UpdateInstructorSchema
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.middleware.error_handler import NotFound, Forbidden
from app.services.instructor_service import InstructorService


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/instructors')
def get_instructors():
    query = Instructor.query.filter_by(tenant_id=g.tenant_id)
    active = request.args.get('active')
    if active:
        query = query.filter_by(is_active=active.lower() == 'true')
    position = request.args.get('position')
    if position:
        query = query.filter_by(position=position)
    query = query.order_by(Instructor.last_name, Instructor.first_name)
    result = paginate_query(query)
    result['data'] = [i.to_dict() for i in result['data']]
    return result


@api_bp.get('/instructors/<instructor_id>')
def get_instructor(instructor_id):
    instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=g.tenant_id).first()
    if not instructor:
        raise NotFound('Instructor not found')
    return instructor.to_dict()


@api_bp.post('/instructors')
def create_instructor():
    _require_admin()
    payload = parse_body(CreateInstructorSchema, request.get_json(silent=True) or {})
    service = InstructorService()
    instructor = service.create_instructor(str(g.tenant_id), payload.model_dump())
    return instructor.to_dict(), 201


@api_bp.put('/instructors/<instructor_id>')
def update_instructor(instructor_id):
    _require_admin()
    payload = parse_body(UpdateInstructorSchema, request.get_json(silent=True) or {})
    service = InstructorService()
    instructor = service.update_instructor(str(g.tenant_id), instructor_id, payload.model_dump(exclude_none=True))
    return instructor.to_dict()


@api_bp.delete('/instructors/<instructor_id>')
def delete_instructor(instructor_id):
    _require_admin()
    service = InstructorService()
    service.delete_instructor(str(g.tenant_id), instructor_id)
    return '', 204


@api_bp.get('/instructors/<instructor_id>/candidates')
def get_instructor_candidates(instructor_id):
    """Get candidates assigned to a specific instructor."""
    instructor = Instructor.query.filter_by(id=instructor_id, tenant_id=g.tenant_id).first()
    if not instructor:
        raise NotFound('Instructor not found')
    # This will be implemented fully when candidate model exists
    # For now return empty list
    return []
