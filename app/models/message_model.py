import uuid
from datetime import datetime
from app.utils.db import db


class Message(db.Model):
    """Message within a conversation."""
    __tablename__ = 'messages'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id'), nullable=False)
    conversation_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    conversation = db.relationship('Conversation', backref=db.backref('messages', lazy='dynamic', order_by='Message.created_at'))
    sender = db.relationship('User', foreign_keys=[sender_id])

    __table_args__ = (
        db.Index('idx_messages_conversation', 'tenant_id', 'conversation_id', 'created_at'),
        db.Index('idx_messages_recipient', 'tenant_id', 'recipient_id', 'is_read'),
    )

    def to_dict(self) -> dict:
        sender_obj = None
        if self.sender:
            sender_obj = {
                'id': str(self.sender.id),
                'fullName': self.sender.full_name,
                'role': self.sender.role,
            }
        return {
            'id': str(self.id),
            'conversationId': str(self.conversation_id),
            'senderId': str(self.sender_id),
            'senderName': self.sender.full_name if self.sender else None,
            'sender': sender_obj,
            'content': self.content,
            'isRead': self.is_read,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
