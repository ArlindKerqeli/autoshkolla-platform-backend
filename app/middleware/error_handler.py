from flask import jsonify
from werkzeug.exceptions import HTTPException

STATUS_CODES = {
    400: 'BAD_REQUEST',
    401: 'UNAUTHORIZED',
    403: 'FORBIDDEN',
    404: 'NOT_FOUND',
    409: 'CONFLICT',
    422: 'UNPROCESSABLE_ENTITY',
    429: 'TOO_MANY_REQUESTS',
    500: 'INTERNAL_ERROR',
}


class ValidationError(Exception):
    """Raised when request validation fails."""
    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.details = details or []
        self.status_code = 400
        self.code = 'VALIDATION_ERROR'


class Unauthorized(Exception):
    """Raised when authentication is required but not provided/valid."""
    def __init__(self, message: str = 'Unauthorized'):
        super().__init__(message)
        self.status_code = 401
        self.code = 'UNAUTHORIZED'


class Forbidden(Exception):
    """Raised when user lacks permission for a resource."""
    def __init__(self, message: str = 'Forbidden'):
        super().__init__(message)
        self.status_code = 403
        self.code = 'FORBIDDEN'


class NotFound(Exception):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = 'Not found'):
        super().__init__(message)
        self.status_code = 404
        self.code = 'NOT_FOUND'


def init_error_handlers(app):
    """
    Initialize error handlers for custom exceptions and HTTP errors.
    """
    @app.errorhandler(ValidationError)
    def _handle_validation_error(err):
        return _json_error(err.status_code, err.code, str(err), err.details)

    @app.errorhandler(Unauthorized)
    def _handle_unauthorized(err):
        return _json_error(err.status_code, err.code, str(err))

    @app.errorhandler(Forbidden)
    def _handle_forbidden(err):
        return _json_error(err.status_code, err.code, str(err))

    @app.errorhandler(NotFound)
    def _handle_not_found(err):
        return _json_error(err.status_code, err.code, str(err))

    @app.errorhandler(HTTPException)
    def _handle_http_error(err):
        status = err.code or 500
        code = STATUS_CODES.get(status, 'INTERNAL_ERROR')
        message = err.description if isinstance(err.description, str) else 'Request failed'
        return _json_error(status, code, message)

    @app.errorhandler(Exception)
    def _handle_unexpected_error(err):
        app.logger.exception('Unhandled exception')
        return _json_error(500, 'INTERNAL_ERROR', str(err))


def _json_error(status: int, code: str, message: str, details=None) -> tuple:
    """
    Format error response as JSON.
    """
    payload = {
        'success': False,
        'error': {
            'code': code,
            'message': message,
        },
    }
    if details:
        payload['error']['details'] = details
    response = jsonify(payload)
    response.status_code = status
    return response
