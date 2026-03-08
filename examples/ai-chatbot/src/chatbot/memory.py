"""Conversation memory: save and load conversations as JSON."""

import json
from datetime import datetime, timezone
from pathlib import Path

from chatbot.models import Conversation, Message, Persona


def save_conversation(conv: Conversation, directory: Path) -> Path:
    """Save a conversation to a JSON file.

    Returns the path to the saved file.
    """
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S_%f")
    slug = conv.persona.name.lower().replace(" ", "-")
    path = directory / f"{timestamp}_{slug}.json"

    data = {
        "persona": {
            "name": conv.persona.name,
            "description": conv.persona.description,
            "system_prompt": conv.persona.system_prompt,
        },
        "messages": [{"role": m.role, "content": m.content} for m in conv.messages],
        "started_at": conv.started_at.isoformat(),
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return path


def load_conversation(path: Path) -> Conversation:
    """Load a conversation from a JSON file."""
    data = json.loads(path.read_text())
    persona = Persona(**data["persona"])
    messages = [Message(**m) for m in data["messages"]]
    started_at = datetime.fromisoformat(data["started_at"])
    return Conversation(persona=persona, messages=messages, started_at=started_at)


def list_conversations(directory: Path) -> list[Path]:
    """List saved conversation files, newest first."""
    if not directory.exists():
        return []
    files = sorted(directory.glob("*.json"), reverse=True)
    return files
