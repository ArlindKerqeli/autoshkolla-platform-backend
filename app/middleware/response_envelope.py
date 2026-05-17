from flask import jsonify, make_response


def init_response_envelope(app):
    """
    Initialize response envelope middleware.
    Wraps all successful JSON responses in a standard envelope format:
    {
        "success": true,
        "data": {...} or [...]
    }
    """
    @app.after_request
    def _wrap_response(response):
        # Don't wrap error responses
        if response.status_code >= 400:
            return response

        # Don't wrap streaming or passthrough responses
        if response.is_streamed or response.direct_passthrough:
            return response

        # Don't wrap non-JSON responses
        if not response.is_json:
            return response

        # Don't wrap if explicitly bypassed
        if response.headers.get('X-Bypass-Envelope') == '1':
            return response

        data = response.get_json(silent=True)

        # Don't wrap if already wrapped
        if isinstance(data, dict) and 'success' in data:
            return response

        # Handle paginated responses (data + meta)
        if isinstance(data, dict) and 'data' in data and 'meta' in data and isinstance(data.get('data'), list):
            meta = data['meta']
            pagination = {
                'page': meta.get('page'),
                'perPage': meta.get('per_page'),
                'total': meta.get('total'),
                'totalPages': meta.get('pages'),
            }
            payload = {'success': True, 'data': data['data'], 'pagination': pagination}
        else:
            # Wrap single object or array responses
            payload = {'success': True, 'data': data}

        wrapped = make_response(jsonify(payload), response.status_code)
        return wrapped
