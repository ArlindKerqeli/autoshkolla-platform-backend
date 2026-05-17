"""Integration tests for messages/conversations API endpoints."""
import uuid
import pytest
from app.utils.db import db as _db
from app.models.conversation_model import Conversation
from app.models.message_model import Message
from tests.conftest import auth_header


class TestConversations:
    def test_list_conversations(self, client, admin_token, admin_user):
        resp = client.get('/api/v1/conversations', headers=auth_header(admin_token))
        assert resp.status_code == 200

    def test_create_conversation(self, client, admin_token, admin_user, instructor_user):
        resp = client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Test mesazh',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'Pershendetje, si jeni?',
        })
        assert resp.status_code == 201

    def test_get_conversation_messages(self, client, admin_token, admin_user, instructor_user):
        # Create a conversation first
        create_resp = client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Test',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'Hello',
        })
        conv = create_resp.get_json()
        conv_id = conv.get('id') or conv.get('data', {}).get('id')
        resp = client.get(
            f'/api/v1/conversations/{conv_id}/messages',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

    def test_get_conversation_messages_not_found(self, client, admin_token):
        resp = client.get(
            f'/api/v1/conversations/{uuid.uuid4()}/messages',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_send_message(self, client, admin_token, admin_user, instructor_user):
        create_resp = client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Thread',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'First message',
        })
        conv = create_resp.get_json()
        conv_id = conv.get('id') or conv.get('data', {}).get('id')
        resp = client.post(
            f'/api/v1/conversations/{conv_id}/messages',
            headers=auth_header(admin_token),
            json={'content': 'Second message'},
        )
        assert resp.status_code == 201

    def test_send_message_conv_not_found(self, client, admin_token):
        resp = client.post(
            f'/api/v1/conversations/{uuid.uuid4()}/messages',
            headers=auth_header(admin_token),
            json={'content': 'Test'},
        )
        assert resp.status_code == 404


    def test_mark_conversation_read(self, client, admin_token, instructor_token, admin_user, instructor_user):
        # Admin creates a conversation with instructor
        create_resp = client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Mark read test',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'Unread message for instructor',
        })
        conv = create_resp.get_json()
        conv_id = conv.get('id') or conv.get('data', {}).get('id')

        # Instructor marks conversation as read
        resp = client.put(
            f'/api/v1/conversations/{conv_id}/read',
            headers=auth_header(instructor_token),
        )
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'count' in result
        assert result['count'] >= 1

    def test_mark_conversation_read_not_found(self, client, admin_token):
        resp = client.put(
            f'/api/v1/conversations/{uuid.uuid4()}/read',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_conversation_last_message_is_object(self, client, admin_token, admin_user, instructor_user):
        # Create a conversation with a message
        client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Last message test',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'Check last message format',
        })
        # Fetch conversations
        resp = client.get('/api/v1/conversations', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        convs = data.get('data', data)
        if isinstance(convs, list) and len(convs) > 0:
            last_msg = convs[0].get('lastMessage')
            assert last_msg is not None
            assert isinstance(last_msg, dict), 'lastMessage should be an object, not a string'
            assert 'content' in last_msg
            assert 'senderId' in last_msg
            assert 'senderName' in last_msg
            assert 'createdAt' in last_msg

    def test_message_to_dict_has_sender_object(self, client, admin_token, admin_user, instructor_user):
        # Create a conversation with a message
        create_resp = client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Sender object test',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'Test sender serialization',
        })
        conv = create_resp.get_json()
        conv_id = conv.get('id') or conv.get('data', {}).get('id')
        # Get messages
        msgs_resp = client.get(
            f'/api/v1/conversations/{conv_id}/messages',
            headers=auth_header(admin_token),
        )
        data = msgs_resp.get_json()
        msg_list = data.get('data', data)
        if isinstance(msg_list, list) and len(msg_list) > 0:
            msg = msg_list[0]
            assert 'sender' in msg
            assert msg['sender'] is not None
            assert 'fullName' in msg['sender']
            assert 'id' in msg['sender']
            assert msg['senderName'] is not None


class TestMessages:
    def test_mark_message_read(self, client, admin_token, admin_user, instructor_user):
        create_resp = client.post('/api/v1/conversations', headers=auth_header(admin_token), json={
            'subject': 'Read test',
            'recipientId': str(instructor_user.id),
            'initialMessage': 'Message to read',
        })
        conv = create_resp.get_json()
        conv_id = conv.get('id') or conv.get('data', {}).get('id')
        # Get messages to find the message ID
        msgs_resp = client.get(
            f'/api/v1/conversations/{conv_id}/messages',
            headers=auth_header(admin_token),
        )
        msgs = msgs_resp.get_json()
        msg_list = msgs.get('data', msgs)
        if isinstance(msg_list, list) and len(msg_list) > 0:
            msg_id = msg_list[0].get('id')
            resp = client.put(
                f'/api/v1/messages/{msg_id}/read',
                headers=auth_header(admin_token),
            )
            assert resp.status_code == 200

    def test_mark_message_read_not_found(self, client, admin_token):
        resp = client.put(
            f'/api/v1/messages/{uuid.uuid4()}/read',
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 404

    def test_unread_count(self, client, admin_token, admin_user):
        resp = client.get('/api/v1/messages/unread-count', headers=auth_header(admin_token))
        assert resp.status_code == 200
        data = resp.get_json()
        result = data.get('data', data)
        assert 'unreadCount' in result
