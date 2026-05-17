from flask import request, g
from app.api import api_bp
from app.schemas.auth import LoginSchema, RefreshSchema
from app.utils.validation import parse_body
from app.services.auth_service import AuthService
from app.middleware.error_handler import Unauthorized


@api_bp.post('/auth/login')
def login():
    """
    Login endpoint.
    Accepts username and password, returns access and refresh tokens.
    """
    payload = parse_body(LoginSchema, request.get_json(silent=True) or {})
    service = AuthService()
    data = service.login(payload.username, payload.password)
    return data


@api_bp.post('/auth/refresh')
def refresh():
    """
    Refresh access token endpoint.
    Accepts a refresh token, returns a new access token.
    """
    payload = parse_body(RefreshSchema, request.get_json(silent=True) or {})
    service = AuthService()
    data = service.refresh(payload.refreshToken)
    return data


@api_bp.post('/auth/logout')
def logout():
    """
    Logout endpoint.
    Requires authentication. Returns 204 No Content.
    """
    if not getattr(g, 'current_user', None):
        raise Unauthorized('Not authenticated')
    return ('', 204)


@api_bp.get('/auth/me')
def me():
    """
    Get current user endpoint.
    Requires authentication. Returns current user details.
    """
    if not getattr(g, 'current_user', None):
        raise Unauthorized('Not authenticated')
    service = AuthService()
    data = service.get_me(g.current_user['sub'], g.current_user['tenantId'])
    return data
