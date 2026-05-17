from datetime import datetime
from flask import request, g
from sqlalchemy import func
from app.api import api_bp
from app.models.conversation_model import Conversation
from app.models.message_model import Message
from app.models.user_model import User
from app.schemas.messages import CreateConversationSchema, SendMessageSchema
from app.utils.validation import parse_body
from app.utils.pagination import paginate_query
from app.middleware.error_handler import NotFound, Forbidden, ValidationError
from app.utils.db import db


@api_bp.get('/conversations')
def get_conversations():
    user_id = g.current_user['sub']
    # Get conversations where current user is a participant
    query = Conversation.query.filter(
        Conversation.tenant_id == g.tenant_id,
        Conversation.participant_ids.any(user_id)
    ).order_by(Conversation.last_message_at.desc().nullslast())

    result = paginate_query(query)
    conv_list = result['data']
    if not conv_list:
        result['data'] = []
        return result

    conv_ids = [conv.id for conv in conv_list]

    # Subquery: unread count per conversation (messages not sent by current user and unread)
    unread_counts = dict(
        db.session.query(
            Message.conversation_id,
            func.count(Message.id)
        ).filter(
            Message.conversation_id.in_(conv_ids),
            Message.sender_id != user_id,
            Message.is_read == False  # noqa: E712
        ).group_by(Message.conversation_id).all()
    )

    # Subquery: last message per conversation (with sender info)
    # First get the max created_at per conversation
    latest_ts_subq = db.session.query(
        Message.conversation_id,
        func.max(Message.created_at).label('max_created_at')
    ).filter(
        Message.conversation_id.in_(conv_ids)
    ).group_by(Message.conversation_id).subquery()

    # Then join back to get the actual message details + sender name
    last_messages_rows = db.session.query(
        Message.conversation_id,
        Message.content,
        Message.sender_id,
        Message.created_at,
        User.full_name,
    ).join(
        latest_ts_subq,
        db.and_(
            Message.conversation_id == latest_ts_subq.c.conversation_id,
            Message.created_at == latest_ts_subq.c.max_created_at
        )
    ).outerjoin(
        User, Message.sender_id == User.id
    ).all()

    last_messages = {}
    for row in last_messages_rows:
        last_messages[row.conversation_id] = {
            'content': row.content[:100] if row.content else None,
            'senderId': str(row.sender_id) if row.sender_id else None,
            'senderName': row.full_name,
            'createdAt': row.created_at.isoformat() if row.created_at else None,
        }

    # Build response using the pre-fetched data
    conversations = []
    for conv in conv_list:
        conv_dict = conv.to_dict()
        conv_dict['unreadCount'] = unread_counts.get(conv.id, 0)
        conv_dict['lastMessage'] = last_messages.get(conv.id)
        conversations.append(conv_dict)

    result['data'] = conversations
    return result


@api_bp.post('/conversations')
def create_conversation():
    payload = parse_body(CreateConversationSchema, request.get_json(silent=True) or {})
    user_id = g.current_user['sub']

    recipient_id = payload.recipientId
    if not recipient_id:
        # Auto-resolve: instructors message the first admin, admins need a recipientId
        role = g.current_user.get('role')
        if role == 'instructor':
            admin = User.query.filter_by(
                tenant_id=g.tenant_id, role='administrator', is_active=True
            ).first()
            if not admin:
                raise ValidationError('No administrator found to message')
            recipient_id = str(admin.id)
        else:
            raise ValidationError('recipientId is required')

    conv = Conversation(
        tenant_id=g.tenant_id,
        subject=payload.subject,
        participant_ids=[user_id, recipient_id],
        created_by=user_id,
        last_message_at=datetime.utcnow(),
    )
    db.session.add(conv)
    db.session.flush()

    msg = Message(
        tenant_id=g.tenant_id,
        conversation_id=conv.id,
        sender_id=user_id,
        recipient_id=recipient_id,
        content=payload.initialMessage,
    )
    db.session.add(msg)
    db.session.commit()

    return conv.to_dict(), 201


@api_bp.get('/conversations/<conversation_id>/messages')
def get_conversation_messages(conversation_id):
    conv = Conversation.query.filter_by(id=conversation_id, tenant_id=g.tenant_id).first()
    if not conv:
        raise NotFound('Conversation not found')

    # Verify user is participant
    user_id = g.current_user['sub']
    if user_id not in [str(pid) for pid in conv.participant_ids]:
        raise Forbidden('Not a participant in this conversation')

    query = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.created_at.asc())
    result = paginate_query(query)
    result['data'] = [m.to_dict() for m in result['data']]
    return result


@api_bp.post('/conversations/<conversation_id>/messages')
def send_message(conversation_id):
    conv = Conversation.query.filter_by(id=conversation_id, tenant_id=g.tenant_id).first()
    if not conv:
        raise NotFound('Conversation not found')

    user_id = g.current_user['sub']
    if user_id not in [str(pid) for pid in conv.participant_ids]:
        raise Forbidden('Not a participant in this conversation')

    payload = parse_body(SendMessageSchema, request.get_json(silent=True) or {})

    # Determine recipient (the other participant)
    recipient_id = None
    for pid in conv.participant_ids:
        if str(pid) != user_id:
            recipient_id = str(pid)
            break

    msg = Message(
        tenant_id=g.tenant_id,
        conversation_id=conv.id,
        sender_id=user_id,
        recipient_id=recipient_id,
        content=payload.content,
    )
    db.session.add(msg)
    conv.last_message_at = datetime.utcnow()
    db.session.commit()

    return msg.to_dict(), 201


@api_bp.put('/conversations/<conversation_id>/read')
def mark_conversation_read(conversation_id):
    """Mark all messages in a conversation as read for the current user."""
    user_id = g.current_user['sub']
    conv = Conversation.query.filter_by(
        id=conversation_id, tenant_id=g.tenant_id
    ).first()
    if not conv:
        raise NotFound('Conversation not found')

    # Verify user is participant
    if user_id not in [str(pid) for pid in conv.participant_ids]:
        raise Forbidden('Not a participant in this conversation')

    # Mark all unread messages NOT sent by current user as read
    now = datetime.utcnow()
    unread = Message.query.filter_by(
        conversation_id=conversation_id,
        is_read=False
    ).filter(
        Message.sender_id != user_id
    ).all()

    for msg in unread:
        msg.is_read = True
        msg.read_at = now

    db.session.commit()
    return {'count': len(unread)}


@api_bp.put('/messages/<message_id>/read')
def mark_message_read(message_id):
    msg = Message.query.filter_by(id=message_id, tenant_id=g.tenant_id).first()
    if not msg:
        raise NotFound('Message not found')
    msg.is_read = True
    msg.read_at = datetime.utcnow()
    db.session.commit()
    return msg.to_dict()


@api_bp.get('/messages/unread-count')
def get_unread_count():
    user_id = g.current_user['sub']
    count = Message.query.filter(
        Message.tenant_id == g.tenant_id,
        Message.recipient_id == user_id,
        Message.is_read == False
    ).count()
    return {'unreadCount': count}
