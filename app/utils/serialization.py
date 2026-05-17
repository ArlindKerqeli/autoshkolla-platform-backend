import uuid
from datetime import datetime, date


def json_default(obj):
    """
    Default JSON serializer for UUID and datetime objects.
    Used by Flask's json encoder.
    """
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
