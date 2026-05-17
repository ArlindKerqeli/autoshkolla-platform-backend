"""Unit tests for utility modules."""
import uuid
from datetime import timedelta, datetime

import pytest

from app.utils.jwt import parse_duration, encode_access_token, encode_refresh_token, decode_token
from app.utils.validation import BaseSchema, parse_body, parse_query
from app.utils.serialization import json_default
from app.middleware.error_handler import ValidationError


# ---------------------------------------------------------------------------
# JWT utils
# ---------------------------------------------------------------------------
class TestParseDuration:
    def test_minutes(self):
        assert parse_duration('60m') == timedelta(minutes=60)

    def test_hours(self):
        assert parse_duration('2h') == timedelta(hours=2)

    def test_days(self):
        assert parse_duration('7d') == timedelta(days=7)

    def test_invalid_format(self):
        with pytest.raises(ValueError, match='Invalid duration format'):
            parse_duration('abc')

    def test_whitespace_stripped(self):
        assert parse_duration(' 30m ') == timedelta(minutes=30)


class TestJWTTokens:
    def test_encode_decode_access_token(self, app):
        with app.app_context():
            user_id = str(uuid.uuid4())
            tenant_id = str(uuid.uuid4())
            token = encode_access_token(user_id, tenant_id, 'administrator')
            payload = decode_token(token)
            assert payload is not None
            assert payload['sub'] == user_id
            assert payload['tenantId'] == tenant_id
            assert payload['role'] == 'administrator'

    def test_encode_decode_refresh_token(self, app):
        with app.app_context():
            user_id = str(uuid.uuid4())
            token = encode_refresh_token(user_id)
            payload = decode_token(token)
            assert payload is not None
            assert payload['sub'] == user_id
            # Refresh token should not have role/tenantId
            assert 'role' not in payload
            assert 'tenantId' not in payload

    def test_decode_invalid_token(self, app):
        with app.app_context():
            result = decode_token('not.a.valid.jwt')
            assert result is None

    def test_decode_empty_string(self, app):
        with app.app_context():
            result = decode_token('')
            assert result is None


# ---------------------------------------------------------------------------
# Validation utils
# ---------------------------------------------------------------------------
class TestValidation:
    def test_base_schema_extra_forbid(self):
        class TestSchema(BaseSchema):
            name: str

        with pytest.raises(Exception):
            TestSchema(name='ok', extra_field='bad')

    def test_parse_body_success(self, app):
        class TestSchema(BaseSchema):
            name: str
            age: int

        with app.app_context():
            result = parse_body(TestSchema, {'name': 'Test', 'age': 25})
            assert result.name == 'Test'
            assert result.age == 25

    def test_parse_body_validation_error(self, app):
        class TestSchema(BaseSchema):
            name: str
            age: int

        with app.app_context():
            with pytest.raises(ValidationError, match='Validation failed'):
                parse_body(TestSchema, {'name': 'Test'})  # Missing 'age'

    def test_parse_body_strips_whitespace(self, app):
        class TestSchema(BaseSchema):
            name: str

        with app.app_context():
            result = parse_body(TestSchema, {'name': '  hello  '})
            assert result.name == 'hello'

    def test_parse_query_success(self, app):
        class QSchema(BaseSchema):
            page: int = 1

        with app.app_context():
            result = parse_query(QSchema, {'page': 2})
            assert result.page == 2


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------
class TestSerialization:
    def test_uuid_serialization(self):
        uid = uuid.uuid4()
        assert json_default(uid) == str(uid)

    def test_datetime_serialization(self):
        dt = datetime(2026, 3, 1, 12, 0, 0)
        assert json_default(dt) == dt.isoformat()

    def test_date_serialization(self):
        from datetime import date
        d = date(2026, 3, 1)
        assert json_default(d) == d.isoformat()

    def test_unsupported_type(self):
        with pytest.raises(TypeError):
            json_default(set())
