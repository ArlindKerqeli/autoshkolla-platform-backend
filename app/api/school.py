from flask import request, g
from app.api import api_bp
from app.models.tenant_model import Tenant
from app.middleware.error_handler import NotFound, Forbidden
from app.utils.db import db


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/school/profile')
def get_school_profile():
    tenant = Tenant.query.get(g.tenant_id)
    if not tenant:
        raise NotFound('School profile not found')
    return tenant.to_dict()


@api_bp.put('/school/profile')
def update_school_profile():
    _require_admin()
    tenant = Tenant.query.get(g.tenant_id)
    if not tenant:
        raise NotFound('School profile not found')
    data = request.get_json(silent=True) or {}
    updatable = ['name', 'nui', 'tvsh', 'email', 'phone', 'address', 'city',
                 'representative', 'bank_name', 'bank_account', 'license_number']
    camel_map = {
        'name': 'name', 'nui': 'nui', 'tvsh': 'tvsh', 'email': 'email',
        'phone': 'phone', 'address': 'address', 'city': 'city',
        'representative': 'representative', 'bankName': 'bank_name',
        'bankAccount': 'bank_account', 'licenseNumber': 'license_number',
    }
    for camel_key, model_key in camel_map.items():
        if camel_key in data:
            setattr(tenant, model_key, data[camel_key])
    db.session.commit()
    return tenant.to_dict()
