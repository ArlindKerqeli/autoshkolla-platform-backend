import uuid
from datetime import datetime
from app.utils.db import db


class AuditLog(db.Model):
    """Audit log for tracking all user actions and changes."""
    __tablename__ = 'audit_logs'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'))
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(100))
    entity_id = db.Column(db.UUID(as_uuid=True))
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User')

    __table_args__ = (
        db.Index('idx_audit_logs_tenant_date', 'tenant_id', 'created_at'),
        db.Index('idx_audit_logs_user', 'user_id', 'created_at'),
        db.Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
    )

    VALID_ACTIONS = ['create', 'update', 'delete', 'login', 'impersonate']

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'tenantId': self.tenant_id,
            'userId': self.user_id,
            'userName': self.user.full_name if self.user else None,
            'action': self.action,
            'entityType': self.entity_type,
            'entityId': self.entity_id,
            'oldValues': self.old_values,
            'newValues': self.new_values,
            'ipAddress': self.ip_address,
            'createdAt': self.created_at,
        }
