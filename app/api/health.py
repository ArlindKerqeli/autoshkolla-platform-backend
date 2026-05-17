from app.api import api_bp


@api_bp.get('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'service': 'autoshkolla-platform'}
