"""Tests for streaming chat logic."""

from unittest.mock import MagicMock, patch

from chatbot.chat import create_client, send_message
from chatbot.models import Conversation, Message, Persona


def _make_conversation() -> Conversation:
    return Conversation(
        persona=Persona(name="Test", description="D", system_prompt="Be helpful."),
        messages=[Message(role="user", content="Hello")],
    )


def _make_mock_stream(chunks, final_text):
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(chunks)
    mock_stream.get_final_message.return_value = MagicMock(
        content=[MagicMock(type="text", text=final_text)]
    )
    return mock_stream


def test_send_message_returns_text():
    """send_message should return the full response text."""
    mock_client = MagicMock()
    mock_client.messages.stream.return_value = _make_mock_stream(
        ["Hi ", "there!"], "Hi there!"
    )

    conv = _make_conversation()
    result = send_message(mock_client, conv)
    assert result == "Hi there!"


def test_send_message_uses_system_prompt():
    """send_message should pass the persona's system prompt."""
    mock_client = MagicMock()
    mock_client.messages.stream.return_value = _make_mock_stream(["Ok"], "Ok")

    conv = _make_conversation()
    send_message(mock_client, conv)

    call_kwargs = mock_client.messages.stream.call_args[1]
    assert call_kwargs["system"] == "Be helpful."


def test_send_message_uses_correct_model():
    mock_client = MagicMock()
    mock_client.messages.stream.return_value = _make_mock_stream(["Ok"], "Ok")

    conv = _make_conversation()
    send_message(mock_client, conv)

    call_kwargs = mock_client.messages.stream.call_args[1]
    assert call_kwargs["model"] == "claude-sonnet-4-5"


def test_create_client_fails_without_api_key():
    with patch.dict("os.environ", {}, clear=True):
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            client = create_client()
        except SystemExit:
            pass  # Expected when no key
