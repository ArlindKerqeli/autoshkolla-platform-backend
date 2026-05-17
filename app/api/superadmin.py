from flask import request, g, jsonify
from datetime import datetime, timedelta
from app.api import api_bp
from app.models.tenant_model import Tenant
from app.models.user_model import User
from app.models.audit_log_model import AuditLog
from app.models.candidate_model import Candidate
from app.schemas.superadmin import (
    CreateTenantSchema,
    UpdateTenantSchema,
    CreateTenantUserSchema,
    UpdateTenantUserSchema,
    ImpersonateSchema,
)
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.jwt import encode_access_token, encode_refresh_token
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden, Unauthorized
from sqlalchemy import func, and_
from sqlalchemy import or_ as db_or


def _require_super_admin():
    """Require super_admin role for all superadmin endpoints."""
    if g.current_user.get('role') != 'super_admin':
        raise Forbidden('Super administrator access required')


@api_bp.get('/superadmin/tenants')
def list_tenants():
    """List all tenants with pagination and optional search."""
    _require_super_admin()

    query = Tenant.query

    # Optional search by name
    search = request.args.get('search')
    if search:
        search_term = f'%{search}%'
        query = query.filter(Tenant.name.ilike(search_term))

    # Optional filter by active status
    is_active = request.args.get('isActive')
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)

    query = query.order_by(Tenant.created_at.desc())
    result = paginate_query(query)
    result['data'] = [t.to_dict() for t in result['data']]
    return result


@api_bp.get('/superadmin/tenants/<tenant_id>')
def get_tenant(tenant_id):
    """Get tenant details with statistics."""
    _require_super_admin()

    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        raise NotFound('Tenant not found')

    # Get statistics
    user_count = User.query.filter_by(tenant_id=tenant_id).count()
    candidate_count = Candidate.query.filter_by(tenant_id=tenant_id, deleted_at=None).count()

    tenant_data = tenant.to_dict()
    tenant_data['statistics'] = {
        'userCount': user_count,
        'candidateCount': candidate_count,
        'createdAt': tenant.created_at,
        'updatedAt': tenant.updated_at,
    }

    return tenant_data


@api_bp.post('/superadmin/tenants')
def create_tenant():
    """Create a new tenant."""
    _require_super_admin()

    payload = parse_body(CreateTenantSchema, request.get_json(silent=True) or {})

    # Validate slug is unique
    existing_slug = Tenant.query.filter_by(slug=payload.slug).first()
    if existing_slug:
        raise ValidationError(f'Slug "{payload.slug}" is already in use')

    tenant = Tenant(
        name=payload.name,
        slug=payload.slug,
        email=payload.contactEmail,
        phone=payload.contactPhone,
        address=payload.address,
        is_active=True,
    )

    db.session.add(tenant)
    db.session.commit()

    # Log audit
    audit = AuditLog(
        user_id=g.current_user['sub'],
        action='create',
        entity_type='tenant',
        entity_id=tenant.id,
        new_values={'name': tenant.name, 'slug': tenant.slug},
        ip_address=request.remote_addr,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify(tenant.to_dict()), 201


@api_bp.put('/superadmin/tenants/<tenant_id>')
def update_tenant(tenant_id):
    """Update a tenant's information."""
    _require_super_admin()

    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        raise NotFound('Tenant not found')

    payload = parse_body(UpdateTenantSchema, request.get_json(silent=True) or {})

    old_values = {
        'name': tenant.name,
        'email': tenant.email,
        'phone': tenant.phone,
        'address': tenant.address,
        'isActive': tenant.is_active,
    }

    if payload.name is not None:
        tenant.name = payload.name
    if payload.contactEmail is not None:
        tenant.email = payload.contactEmail
    if payload.contactPhone is not None:
        tenant.phone = payload.contactPhone
    if payload.address is not None:
        tenant.address = payload.address
    if payload.isActive is not None:
        tenant.is_active = payload.isActive

    db.session.commit()

    # Log audit
    audit = AuditLog(
        user_id=g.current_user['sub'],
        action='update',
        entity_type='tenant',
        entity_id=tenant.id,
        old_values=old_values,
        new_values={
            'name': tenant.name,
            'email': tenant.email,
            'phone': tenant.phone,
            'address': tenant.address,
            'isActive': tenant.is_active,
        },
        ip_address=request.remote_addr,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify(tenant.to_dict())


@api_bp.delete('/superadmin/tenants/<tenant_id>')
def delete_tenant(tenant_id):
    """Deactivate a tenant (soft delete by setting is_active=False)."""
    _require_super_admin()

    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        raise NotFound('Tenant not found')

    tenant.is_active = False
    db.session.commit()

    # Log audit
    audit = AuditLog(
        user_id=g.current_user['sub'],
        action='update',
        entity_type='tenant',
        entity_id=tenant.id,
        new_values={'isActive': False},
        ip_address=request.remote_addr,
    )
    db.session.add(audit)
    db.session.commit()

    return '', 204


@api_bp.get('/superadmin/tenants/<tenant_id>/users')
def list_tenant_users(tenant_id):
    """List all users for a specific tenant."""
    _require_super_admin()

    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        raise NotFound('Tenant not found')

    query = User.query.filter_by(tenant_id=tenant_id)

    # Optional role filter
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role)

    # Optional search
    search = request.args.get('search')
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            db_or(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term),
                User.username.ilike(search_term),
            )
        )

    query = query.order_by(User.created_at.desc())
    result = paginate_query(query)
    result['data'] = [u.to_dict() for u in result['data']]
    return result


@api_bp.post('/superadmin/tenants/<tenant_id>/users')
def create_tenant_user(tenant_id):
    """Create an administrator user for a specific tenant."""
    _require_super_admin()

    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        raise NotFound('Tenant not found')

    payload = parse_body(CreateTenantUserSchema, request.get_json(silent=True) or {})

    # Validate role
    if payload.role not in User.VALID_ROLES:
        raise ValidationError(f'Invalid role. Valid roles: {", ".join(User.VALID_ROLES)}')

    # Check if email already exists for this tenant
    existing = User.query.filter_by(
        tenant_id=tenant_id, username=payload.email
    ).first()
    if existing:
        raise ValidationError(f'User with email "{payload.email}" already exists in this tenant')

    user = User(
        tenant_id=tenant_id,
        username=payload.email,
        email=payload.email,
        full_name=payload.fullName,
        role=payload.role,
        is_active=True,
    )
    user.set_password(payload.password)

    db.session.add(user)
    db.session.commit()

    # Log audit
    audit = AuditLog(
        tenant_id=tenant_id,
        user_id=g.current_user['sub'],
        action='create',
        entity_type='user',
        entity_id=user.id,
        new_values={'email': user.email, 'fullName': user.full_name, 'role': user.role},
        ip_address=request.remote_addr,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@api_bp.put('/superadmin/tenants/<tenant_id>/users/<user_id>')
def update_tenant_user(tenant_id, user_id):
    """Update a user within a specific tenant."""
    _require_super_admin()

    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        raise NotFound('Tenant not found')

    user = User.query.filter_by(id=user_id, tenant_id=tenant_id).first()
    if not user:
        raise NotFound('User not found')

    payload = parse_body(UpdateTenantUserSchema, request.get_json(silent=True) or {})

    old_values = {
        'fullName': user.full_name,
        'email': user.email,
        'role': user.role,
        'isActive': user.is_active,
    }

    if payload.fullName is not None:
        user.full_name = payload.fullName
    if payload.email is not None:
        user.email = payload.email
        user.username = payload.email
    if payload.role is not None:
        if payload.role not in User.VALID_ROLES:
            raise ValidationError(f'Invalid role. Valid roles: {", ".join(User.VALID_ROLES)}')
        user.role = payload.role
    if payload.isActive is not None:
        user.is_active = payload.isActive
    if payload.password is not None:
        user.set_password(payload.password)

    db.session.commit()

    # Log audit
    audit = AuditLog(
        tenant_id=tenant_id,
        user_id=g.current_user['sub'],
        action='update',
        entity_type='user',
        entity_id=user.id,
        old_values=old_values,
        new_values={'fullName': user.full_name, 'email': user.email, 'role': user.role, 'isActive': user.is_active},
        ip_address=request.remote_addr,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify(user.to_dict())


@api_bp.post('/superadmin/impersonate')
def impersonate():
    """Start impersonation of a target user as super_admin."""
    _require_super_admin()

    payload = parse_body(ImpersonateSchema, request.get_json(silent=True) or {})

    # Find target user
    target_user = User.query.filter_by(id=payload.userId).first()
    if not target_user:
        raise NotFound('Target user not found')

    # Generate JWT with impersonation flag
    payload_dict = {
        'sub': str(target_user.id),
        'tenantId': str(target_user.tenant_id),
        'role': target_user.role,
        'email': target_user.email,
        'impersonatedBy': str(g.current_user['sub']),
        'exp': datetime.utcnow() + timedelta(hours=2),
        'iat': datetime.utcnow(),
    }

    # Use the encode_access_token pattern but with custom payload
    import jwt
    from flask import current_app
    token = jwt.encode(payload_dict, current_app.config['JWT_SECRET'], algorithm='HS256')

    # Log audit
    audit = AuditLog(
        tenant_id=target_user.tenant_id,
        user_id=g.current_user['sub'],
        action='impersonate',
        entity_type='user',
        entity_id=target_user.id,
        new_values={'impersonatedUser': str(target_user.id)},
        ip_address=request.remote_addr,
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'accessToken': token,
        'tokenType': 'Bearer',
        'expiresIn': 7200,
        'impersonatingUser': target_user.to_dict(),
    })


@api_bp.get('/superadmin/stats')
def get_global_stats():
    """Get global statistics for the super admin dashboard."""
    _require_super_admin()

    total_tenants = Tenant.query.count()
    active_tenants = Tenant.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    total_candidates = Candidate.query.filter(Candidate.deleted_at.is_(None)).count()

    # Count candidates by status
    archived_candidates = Candidate.query.filter_by(
        is_archived=True, deleted_at=None
    ).count()
    active_candidates = total_candidates - archived_candidates

    return jsonify({
        'totalTenants': total_tenants,
        'activeTenants': active_tenants,
        'totalUsers': total_users,
        'totalCandidates': total_candidates,
        'activeCandidates': active_candidates,
        'archivedCandidates': archived_candidates,
        'timestamp': datetime.utcnow(),
    })
