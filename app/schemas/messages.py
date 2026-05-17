from typing import Optional
from app.utils.validation import BaseSchema


class CreateConversationSchema(BaseSchema):
    subject: str
    recipientId: str | None = None
    initialMessage: str


class SendMessageSchema(BaseSchema):
    content: str
