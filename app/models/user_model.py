import uuid
import bcrypt
from datetime import datetime
from app.utils.db import db


class User(db.Model):
    """
    User model representing a system user within a tenant.
    Supports multiple roles: super_admin, administrator, instructor, lecturer.
    """
    __tablename__ = 'users'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False, index=True)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    personal_number = db.Column(db.String(20))
    email = db.Column(db.String(200))
    role = db.Column(db.String(50), nullable=False, default='administrator')
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    activation_count = db.Column(db.Integer, default=0)
    last_login_at = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    tenant = db.relationship('Tenant', backref=db.backref('users', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'username', name='uq_users_tenant_username'),
    )

    VALID_ROLES = ['super_admin', 'administrator', 'instructor', 'lecturer']

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password: str) -> None:
        """Hash and set the user's password using bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self, include_tenant: bool = False) -> dict:
        """Convert user to dictionary for JSON serialization."""
        data = {
            'id': self.id,
            'tenantId': self.tenant_id,
            'username': self.username,
            'fullName': self.full_name,
            'personalNumber': self.personal_number,
            'email': self.email,
            'role': self.role,
            'isActive': self.is_active,
            'lastLoginAt': self.last_login_at,
            'createdAt': self.created_at,
        }
        if include_tenant and self.tenant:
            data['tenant'] = self.tenant.to_dict()
        return data
