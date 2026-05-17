import jwt
import re
from datetime import datetime, timedelta
from flask import current_app


def parse_duration(duration_str: str) -> timedelta:
    """
    Parse duration string like '60m', '7d', '1h' to timedelta.
    """
    match = re.match(r'^(\d+)([mhd])$', duration_str.strip())
    if not match:
        raise ValueError(f'Invalid duration format: {duration_str}')

    value, unit = int(match.group(1)), match.group(2)
    if unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    else:
        raise ValueError(f'Unknown duration unit: {unit}')


def encode_access_token(user_id: str, tenant_id: str, role: str) -> str:
    """
    Encode a JWT access token with user_id, tenant_id, and role.
    """
    secret = current_app.config['JWT_SECRET']
    duration_str = current_app.config['JWT_ACCESS_EXPIRATION']
    duration = parse_duration(duration_str)
    expires_at = datetime.utcnow() + duration

    payload = {
        'sub': user_id,
        'tenantId': tenant_id,
        'role': role,
        'exp': expires_at,
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def encode_refresh_token(user_id: str) -> str:
    """
    Encode a JWT refresh token with user_id.
    """
    secret = current_app.config['JWT_SECRET']
    duration_str = current_app.config['JWT_REFRESH_EXPIRATION']
    duration = parse_duration(duration_str)
    expires_at = datetime.utcnow() + duration

    payload = {
        'sub': user_id,
        'exp': expires_at,
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token


def decode_token(token: str) -> dict | None:
    """
    Decode a JWT token and return the payload.
    Returns None if token is invalid or expired.
    """
    try:
        secret = current_app.config['JWT_SECRET']
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, Exception):
        return None
