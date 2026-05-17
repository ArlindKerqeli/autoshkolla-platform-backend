import uuid
from datetime import datetime
from app.utils.db import db


class Conversation(db.Model):
    """Threaded conversation between instructors and admins."""
    __tablename__ = 'conversations'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    participant_ids = db.Column(db.ARRAY(db.UUID(as_uuid=True)), nullable=False)
    last_message_at = db.Column(db.DateTime)
    created_by = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = db.relationship('User', backref='created_conversations')

    __table_args__ = (
        db.Index('idx_conversations_tenant', 'tenant_id', 'last_message_at'),
    )

    def to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'tenantId': str(self.tenant_id),
            'subject': self.subject,
            'participantIds': [str(pid) for pid in self.participant_ids] if self.participant_ids else [],
            'lastMessageAt': self.last_message_at.isoformat() if self.last_message_at else None,
            'createdBy': str(self.created_by),
            'creatorName': self.creator.full_name if self.creator else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
