from flask import request, g
from app.api import api_bp
from app.models.category_model import Category
from app.schemas.categories import CreateCategorySchema, UpdateCategorySchema
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.middleware.error_handler import NotFound, Forbidden
from app.utils.db import db


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/categories')
def get_categories():
    query = Category.query.filter_by(tenant_id=g.tenant_id).order_by(Category.code)
    result = paginate_query(query)
    result['data'] = [c.to_dict() for c in result['data']]
    return result


@api_bp.get('/categories/<category_id>')
def get_category(category_id):
    cat = Category.query.filter_by(id=category_id, tenant_id=g.tenant_id).first()
    if not cat:
        raise NotFound('Category not found')
    return cat.to_dict()


@api_bp.post('/categories')
def create_category():
    _require_admin()
    payload = parse_body(CreateCategorySchema, request.get_json(silent=True) or {})
    cat = Category(
        tenant_id=g.tenant_id,
        code=payload.code,
        description=payload.description,
        verification_text=payload.verificationText,
        verification_code=payload.verificationCode,
        theory_hours=payload.theoryHours,
        practical_hours=payload.practicalHours,
        price=payload.price,
        contract_price=payload.contractPrice,
        is_licensed=payload.isLicensed,
    )
    db.session.add(cat)
    db.session.commit()
    return cat.to_dict(), 201


@api_bp.put('/categories/<category_id>')
def update_category(category_id):
    _require_admin()
    cat = Category.query.filter_by(id=category_id, tenant_id=g.tenant_id).first()
    if not cat:
        raise NotFound('Category not found')
    payload = parse_body(UpdateCategorySchema, request.get_json(silent=True) or {})
    update_data = payload.model_dump(exclude_none=True)
    field_map = {
        'code': 'code', 'description': 'description',
        'verificationText': 'verification_text', 'verificationCode': 'verification_code',
        'theoryHours': 'theory_hours', 'practicalHours': 'practical_hours',
        'price': 'price', 'contractPrice': 'contract_price',
        'isLicensed': 'is_licensed', 'isActive': 'is_active',
    }
    for schema_key, model_key in field_map.items():
        if schema_key in update_data:
            setattr(cat, model_key, update_data[schema_key])
    db.session.commit()
    return cat.to_dict()


@api_bp.delete('/categories/<category_id>')
def delete_category(category_id):
    _require_admin()
    cat = Category.query.filter_by(id=category_id, tenant_id=g.tenant_id).first()
    if not cat:
        raise NotFound('Category not found')
    cat.is_active = False
    db.session.commit()
    return '', 204
