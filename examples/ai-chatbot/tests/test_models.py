"""Tests for chatbot data models."""

from datetime import datetime, timezone

from chatbot.models import Conversation, Message, Persona


def test_persona_has_required_fields():
    p = Persona(name="Test", description="A test persona", system_prompt="Be helpful.")
    assert p.name == "Test"
    assert p.description == "A test persona"
    assert p.system_prompt == "Be helpful."


def test_message_has_role_and_content():
    m = Message(role="user", content="Hello")
    assert m.role == "user"
    assert m.content == "Hello"


def test_conversation_holds_messages():
    persona = Persona(name="P", description="D", system_prompt="S")
    now = datetime.now(timezone.utc)
    conv = Conversation(persona=persona, messages=[], started_at=now)
    conv.messages.append(Message(role="user", content="Hi"))
    assert len(conv.messages) == 1


def test_conversation_to_api_messages():
    persona = Persona(name="P", description="D", system_prompt="S")
    conv = Conversation(
        persona=persona,
        messages=[
            Message(role="user", content="Hi"),
            Message(role="assistant", content="Hello!"),
        ],
        started_at=datetime.now(timezone.utc),
    )
    api_msgs = conv.to_api_messages()
    assert api_msgs == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
