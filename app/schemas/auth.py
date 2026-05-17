from app.utils.validation import BaseSchema


class LoginSchema(BaseSchema):
    """Schema for login request."""
    username: str
    password: str


class RefreshSchema(BaseSchema):
    """Schema for token refresh request."""
    refreshToken: str
