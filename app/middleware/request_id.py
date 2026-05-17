import uuid
from flask import g, request


def init_request_id(app):
    """
    Initialize request ID middleware.
    Adds a unique X-Request-Id to each request and response.
    """
    @app.before_request
    def _set_request_id():
        g.request_id = request.headers.get('X-Request-Id', str(uuid.uuid4()))

    @app.after_request
    def _add_request_id_header(response):
        response.headers['X-Request-Id'] = g.get('request_id', '')
        return response
