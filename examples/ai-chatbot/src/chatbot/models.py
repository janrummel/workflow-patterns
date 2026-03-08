"""Data models for the chatbot."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Persona:
    """A chatbot persona with a system prompt."""

    name: str
    description: str
    system_prompt: str


@dataclass
class Message:
    """A single chat message."""

    role: str
    content: str


@dataclass
class Conversation:
    """A chat conversation with persona and message history."""

    persona: Persona
    messages: list[Message] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)

    def to_api_messages(self) -> list[dict]:
        """Convert messages to Anthropic API format."""
        return [{"role": m.role, "content": m.content} for m in self.messages]
