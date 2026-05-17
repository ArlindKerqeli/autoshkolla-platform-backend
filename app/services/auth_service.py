from datetime import datetime
from app.models.user_model import User
from app.models.tenant_model import Tenant
from app.utils.jwt import encode_access_token, encode_refresh_token, decode_token
from app.middleware.error_handler import Unauthorized, NotFound
from app.utils.db import db


class AuthService:
    """Service for authentication and authorization operations."""

    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user with username and password.
        Returns tokens and user details on success.
        """
        user = User.query.filter_by(username=username, is_active=True).first()
        if not user or not user.check_password(password):
            raise Unauthorized('Invalid username or password')

        tenant = Tenant.query.get(user.tenant_id)
        if not tenant or not tenant.is_active:
            raise Unauthorized('Tenant is inactive')

        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        # Generate tokens
        access_token = encode_access_token(str(user.id), str(user.tenant_id), user.role)
        refresh_token = encode_refresh_token(str(user.id))

        return {
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'user': user.to_dict(include_tenant=True),
        }

    def refresh(self, refresh_token: str) -> dict:
        """
        Refresh access token using a refresh token.
        Returns a new access token.
        """
        payload = decode_token(refresh_token)
        if not payload or not payload.get('sub'):
            raise Unauthorized('Invalid refresh token')

        user = User.query.get(payload['sub'])
        if not user or not user.is_active:
            raise Unauthorized('User not found or inactive')

        # Generate new access token
        access_token = encode_access_token(str(user.id), str(user.tenant_id), user.role)
        return {'accessToken': access_token}

    def get_me(self, user_id: str, tenant_id: str) -> dict:
        """
        Get current authenticated user details.
        """
        user = User.query.get(user_id)
        if not user:
            raise NotFound('User not found')
        return user.to_dict(include_tenant=True)
