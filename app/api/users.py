from flask import request, g, jsonify
from app.api import api_bp
from app.models.user_model import User
from app.schemas.users import CreateUserSchema, UpdateUserSchema, ChangePasswordSchema
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden
from sqlalchemy import or_ as db_or


def _require_admin():
    """Require administrator role."""
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


@api_bp.get('/users')
def list_users():
    """List users for tenant with optional filtering."""
    _require_admin()

    query = User.query.filter_by(tenant_id=g.tenant_id)

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
                User.username.ilike(search_term),
                User.email.ilike(search_term),
            )
        )

    # Optional is_active filter
    is_active = request.args.get('isActive')
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter_by(is_active=is_active_bool)

    query = query.order_by(User.created_at.desc())
    result = paginate_query(query)
    result['data'] = [u.to_dict() for u in result['data']]
    return result


@api_bp.get('/users/<user_id>')
def get_user(user_id):
    """Get a specific user."""
    user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id).first()
    if not user:
        raise NotFound('User not found')

    return jsonify(user.to_dict())


@api_bp.post('/users')
def create_user():
    """Create a new user."""
    _require_admin()
    payload = parse_body(CreateUserSchema, request.get_json(silent=True) or {})

    # Validate role
    if payload.role not in User.VALID_ROLES:
        raise ValidationError(f'Invalid role. Valid roles: {", ".join(User.VALID_ROLES)}')

    # Check if username already exists for this tenant
    existing = User.query.filter_by(
        tenant_id=g.tenant_id, username=payload.email
    ).first()
    if existing:
        raise ValidationError(f'User with email "{payload.email}" already exists in this tenant')

    user = User(
        tenant_id=g.tenant_id,
        username=payload.email,
        email=payload.email,
        full_name=payload.fullName,
        role=payload.role,
        is_active=True,
    )
    user.set_password(payload.password)

    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@api_bp.put('/users/<user_id>')
def update_user(user_id):
    """Update a user."""
    _require_admin()
    user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id).first()
    if not user:
        raise NotFound('User not found')

    payload = parse_body(UpdateUserSchema, request.get_json(silent=True) or {})

    # Prevent updating own role to non-admin
    if payload.role is not None and str(user.id) == str(g.current_user['sub']):
        if payload.role not in ('administrator', 'super_admin'):
            raise ValidationError('Cannot downgrade your own role')

    if payload.email is not None:
        # Check if new email already exists
        existing = User.query.filter_by(
            tenant_id=g.tenant_id, username=payload.email
        ).filter(User.id != user_id).first()
        if existing:
            raise ValidationError(f'User with email "{payload.email}" already exists in this tenant')
        user.email = payload.email
        user.username = payload.email

    if payload.fullName is not None:
        user.full_name = payload.fullName

    if payload.role is not None:
        if payload.role not in User.VALID_ROLES:
            raise ValidationError(f'Invalid role. Valid roles: {", ".join(User.VALID_ROLES)}')
        user.role = payload.role

    if payload.isActive is not None:
        user.is_active = payload.isActive

    db.session.commit()
    return jsonify(user.to_dict())


@api_bp.delete('/users/<user_id>')
def delete_user(user_id):
    """Deactivate a user (soft delete by setting is_active=False)."""
    _require_admin()

    user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id).first()
    if not user:
        raise NotFound('User not found')

    # Prevent deactivating yourself
    if str(user.id) == str(g.current_user['sub']):
        raise ValidationError('Cannot deactivate your own account')

    user.is_active = False
    db.session.commit()
    return '', 204


@api_bp.put('/users/<user_id>/password')
def change_password(user_id):
    """Change a user's password (admin only)."""
    _require_admin()

    user = User.query.filter_by(id=user_id, tenant_id=g.tenant_id).first()
    if not user:
        raise NotFound('User not found')

    payload = parse_body(ChangePasswordSchema, request.get_json(silent=True) or {})

    if not payload.password:
        raise ValidationError('Password cannot be empty')

    if len(payload.password) < 6:
        raise ValidationError('Password must be at least 6 characters')

    user.set_password(payload.password)
    db.session.commit()

    return jsonify(user.to_dict())
