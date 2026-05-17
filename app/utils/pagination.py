from flask import request


DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 25
MAX_PER_PAGE = 100


def paginate_query(query, page=None, per_page=None) -> dict:
    """
    Paginate a SQLAlchemy query and return paginated results with metadata.
    Accepts optional page and per_page overrides; otherwise reads from request args.
    """
    if page is None:
        page = request.args.get('page', DEFAULT_PAGE, type=int)
    if per_page is None:
        per_page = request.args.get('per_page', None, type=int)
        if per_page is None:
            per_page = request.args.get('limit', DEFAULT_PER_PAGE, type=int)

    per_page = min(per_page, MAX_PER_PAGE)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        'data': pagination.items,
        'meta': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
        }
    }
