from flask import g, request
from app.utils.jwt import decode_token

ACCESS_TOKEN_COOKIE = 'autoshkolla_access_token'
REFRESH_TOKEN_COOKIE = 'autoshkolla_refresh_token'


def init_auth_context(app):
    """
    Initialize authentication context middleware.
    Extracts JWT token from Authorization header or cookies and sets g.current_user.
    """
    @app.before_request
    def _load_auth_context():
        g._refresh_access_token = None
        token = _extract_token(request)
        if token:
            payload = decode_token(token)
            if _is_valid_payload(payload):
                g.current_user = payload
                g.tenant_id = payload.get('tenantId')
                return
        g.current_user = None
        g.tenant_id = None


def _is_valid_payload(payload: dict | None) -> bool:
    """
    Verify that the JWT payload contains all required fields.
    """
    if not payload:
        return False
    return bool(payload.get('sub') and payload.get('tenantId') and payload.get('role'))


def _extract_token(req) -> str | None:
    """
    Extract JWT token from Authorization header or cookies.
    """
    auth_header = req.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ', 1)[1].strip()
    return req.cookies.get(ACCESS_TOKEN_COOKIE)
