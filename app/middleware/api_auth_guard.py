from flask import g, request
from app.middleware.error_handler import Unauthorized

PUBLIC_PATHS = {
    '/api/v1/health',
    '/api/v1/auth/login',
    '/api/v1/auth/refresh',
}


def init_api_auth_guard(app):
    """
    Initialize API authentication guard middleware.
    Requires authentication for all /api/v1/* routes except those in PUBLIC_PATHS.
    """
    @app.before_request
    def _enforce_api_auth():
        if request.method == 'OPTIONS':
            return
        if not request.path.startswith('/api/v1'):
            return
        if request.path in PUBLIC_PATHS:
            return
        if not getattr(g, 'current_user', None):
            raise Unauthorized('Not authenticated')
