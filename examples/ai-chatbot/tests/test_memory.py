"""Tests for conversation memory (save/load)."""

import json
from datetime import datetime, timezone
from pathlib import Path

from chatbot.memory import list_conversations, load_conversation, save_conversation
from chatbot.models import Conversation, Message, Persona


def _make_conversation() -> Conversation:
    return Conversation(
        persona=Persona(name="Test", description="D", system_prompt="S"),
        messages=[
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
        ],
        started_at=datetime(2026, 3, 8, 12, 0, 0, tzinfo=timezone.utc),
    )


def test_save_creates_json_file(tmp_path):
    conv = _make_conversation()
    path = save_conversation(conv, tmp_path)
    assert path.exists()
    assert path.suffix == ".json"


def test_save_contains_correct_data(tmp_path):
    conv = _make_conversation()
    path = save_conversation(conv, tmp_path)
    data = json.loads(path.read_text())
    assert data["persona"]["name"] == "Test"
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    assert "started_at" in data


def test_load_restores_conversation(tmp_path):
    conv = _make_conversation()
    path = save_conversation(conv, tmp_path)
    loaded = load_conversation(path)
    assert loaded.persona.name == "Test"
    assert len(loaded.messages) == 2
    assert loaded.messages[1].content == "Hi there!"


def test_list_conversations_finds_json_files(tmp_path):
    conv = _make_conversation()
    save_conversation(conv, tmp_path)
    save_conversation(conv, tmp_path)  # second file
    files = list_conversations(tmp_path)
    assert len(files) >= 2


def test_list_conversations_empty_dir(tmp_path):
    files = list_conversations(tmp_path)
    assert files == []
