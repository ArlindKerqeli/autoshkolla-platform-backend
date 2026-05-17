import os


class Config:
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')

    # PostgreSQL
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://autoshkolla:dev_password@localhost:5432/autoshkolla_platform'
    )

    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'change-me')
    JWT_ACCESS_EXPIRATION = os.getenv('JWT_ACCESS_EXPIRATION', '60m')
    JWT_REFRESH_EXPIRATION = os.getenv('JWT_REFRESH_EXPIRATION', '7d')

    # Comma-separated list of allowed origins. In production this should include
    # the Vercel URL(s) of the frontend (and any custom domain).
    CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'http://localhost:3000')

    @classmethod
    def cors_origins(cls) -> list[str]:
        """Parse CORS_ORIGIN as a comma-separated list of origins."""
        raw = cls.CORS_ORIGIN or ''
        return [o.strip() for o in raw.split(',') if o.strip()]
