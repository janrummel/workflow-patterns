# AI Chatbot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a terminal-based streaming chatbot with persona presets and conversation persistence as the second runnable example.

**Architecture:** Interactive CLI selects a persona (system prompt), then enters a streaming chat loop using `client.messages.stream()`. Conversations are persisted as JSON. Pattern: `trigger → ai → data → deliver`.

**Tech Stack:** Python 3.12+, `anthropic` SDK (streaming), `pytest`, `uv`

---

### Task 1: Project scaffolding

**Files:**
- Create: `examples/ai-chatbot/pyproject.toml`
- Create: `examples/ai-chatbot/.env.example`
- Create: `examples/ai-chatbot/.gitignore`
- Create: `examples/ai-chatbot/src/chatbot/__init__.py`

**Step 1: Create pyproject.toml**

```toml
[project]
name = "ai-chatbot"
version = "0.1.0"
description = "AI Chatbot workflow: trigger -> ai -> data -> deliver"
requires-python = ">=3.12"
dependencies = [
    "anthropic",
]

[dependency-groups]
dev = ["pytest"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/chatbot"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: Create .env.example**

```
# Copy this file to .env and add your key:
#   cp .env.example .env
#
# .env is in .gitignore — it will never be committed.
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Step 3: Create .gitignore**

```
.venv/
conversations/
__pycache__/
*.egg-info/
.env
```

**Step 4: Create empty `src/chatbot/__init__.py`**

**Step 5: Run `uv sync` to verify project setup**

Run: `cd examples/ai-chatbot && uv sync`
Expected: Resolves and installs `anthropic` + dependencies

**Step 6: Commit**

```bash
git add examples/ai-chatbot/
git commit -m "Scaffold AI Chatbot example project"
```

---

### Task 2: Data models

**Files:**
- Create: `examples/ai-chatbot/tests/test_models.py`
- Create: `examples/ai-chatbot/src/chatbot/models.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'chatbot.models'`

**Step 3: Write implementation**

```python
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
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_models.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add examples/ai-chatbot/src/chatbot/models.py examples/ai-chatbot/tests/test_models.py
git commit -m "Add chatbot data models with tests"
```

---

### Task 3: Persona presets

**Files:**
- Create: `examples/ai-chatbot/tests/test_personas.py`
- Create: `examples/ai-chatbot/src/chatbot/personas.py`

**Step 1: Write failing tests**

```python
"""Tests for persona presets."""

from chatbot.models import Persona
from chatbot.personas import PERSONAS, get_persona


def test_has_five_personas():
    assert len(PERSONAS) == 5


def test_all_personas_are_persona_instances():
    for p in PERSONAS:
        assert isinstance(p, Persona)


def test_all_personas_have_system_prompts():
    for p in PERSONAS:
        assert len(p.system_prompt) > 50, f"{p.name} system prompt too short"


def test_all_personas_have_unique_names():
    names = [p.name for p in PERSONAS]
    assert len(names) == len(set(names))


def test_get_persona_by_index():
    p = get_persona(0)
    assert p == PERSONAS[0]


def test_get_persona_out_of_range_returns_first():
    p = get_persona(99)
    assert p == PERSONAS[0]
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_personas.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Persona presets for the chatbot."""

from chatbot.models import Persona

PERSONAS = [
    Persona(
        name="Code Reviewer",
        description="Code quality, security, best practices",
        system_prompt=(
            "You are a senior code reviewer. Analyze code for correctness, security "
            "vulnerabilities, performance issues, and maintainability. Be specific: "
            "reference line numbers or patterns. Suggest concrete improvements, not just "
            "problems. Prioritize issues by severity. If the code is good, say so."
        ),
    ),
    Persona(
        name="Writing Coach",
        description="Clarity, structure, tone",
        system_prompt=(
            "You are a writing coach focused on clarity and impact. Help improve structure, "
            "eliminate jargon, strengthen arguments, and find the right tone for the audience. "
            "When reviewing text, be specific about what works and what doesn't. Suggest "
            "rewrites for weak passages rather than just pointing out problems."
        ),
    ),
    Persona(
        name="Research Assistant",
        description="Facts, sources, systematic analysis",
        system_prompt=(
            "You are a research assistant. Help analyze topics systematically: identify key "
            "questions, evaluate evidence, distinguish facts from assumptions, and suggest "
            "further research directions. Be explicit about confidence levels and what you "
            "don't know. Cite specific concepts or frameworks when relevant."
        ),
    ),
    Persona(
        name="Explain Like I'm 5",
        description="Complex topics made simple",
        system_prompt=(
            "You explain complex topics in simple terms using everyday analogies and examples. "
            "Avoid jargon. Use short sentences. Build understanding step by step — start with "
            "the core idea, then add layers. If the user asks a follow-up, go one level deeper "
            "while staying accessible."
        ),
    ),
    Persona(
        name="Debate Partner",
        description="Counterarguments, find weaknesses",
        system_prompt=(
            "You are a rigorous debate partner. When the user presents an argument, steelman "
            "it first (show you understand it), then challenge it with the strongest possible "
            "counterarguments. Identify hidden assumptions, logical gaps, and overlooked "
            "perspectives. Be intellectually honest — if an argument is strong, acknowledge it."
        ),
    ),
]


def get_persona(index: int) -> Persona:
    """Get a persona by index, defaulting to first if out of range."""
    if 0 <= index < len(PERSONAS):
        return PERSONAS[index]
    return PERSONAS[0]
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_personas.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add examples/ai-chatbot/src/chatbot/personas.py examples/ai-chatbot/tests/test_personas.py
git commit -m "Add 5 persona presets with system prompts"
```

---

### Task 4: Conversation memory (save/load)

**Files:**
- Create: `examples/ai-chatbot/tests/test_memory.py`
- Create: `examples/ai-chatbot/src/chatbot/memory.py`

**Step 1: Write failing tests**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_memory.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
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
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
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
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_memory.py -v`
Expected: 5 passed

**Step 5: Commit**

```bash
git add examples/ai-chatbot/src/chatbot/memory.py examples/ai-chatbot/tests/test_memory.py
git commit -m "Add conversation save/load with JSON persistence"
```

---

### Task 5: Display formatting

**Files:**
- Create: `examples/ai-chatbot/tests/test_display.py`
- Create: `examples/ai-chatbot/src/chatbot/display.py`

**Step 1: Write failing tests**

```python
"""Tests for terminal display formatting."""

from chatbot.display import format_header, format_persona_menu, format_welcome
from chatbot.models import Persona


def test_format_header():
    result = format_header("AI Chatbot")
    assert "AI Chatbot" in result
    assert "╔" in result


def test_format_persona_menu():
    personas = [
        Persona(name="Coder", description="Writes code", system_prompt="S"),
        Persona(name="Writer", description="Writes text", system_prompt="S"),
    ]
    result = format_persona_menu(personas)
    assert "1." in result
    assert "2." in result
    assert "Coder" in result
    assert "Writes text" in result


def test_format_welcome():
    persona = Persona(name="Research Assistant", description="D", system_prompt="S")
    result = format_welcome(persona)
    assert "Research Assistant" in result
    assert "/quit" in result
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_display.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Terminal display formatting for the chatbot."""

from chatbot.models import Persona


def format_header(title: str) -> str:
    """Format a boxed header."""
    width = 42
    lines = [
        "",
        "╔" + "═" * width + "╗",
        "║" + title.center(width) + "║",
        "╚" + "═" * width + "╝",
        "",
    ]
    return "\n".join(lines)


def format_persona_menu(personas: list[Persona]) -> str:
    """Format the persona selection menu."""
    lines = ["Choose a persona:", ""]
    for i, p in enumerate(personas, 1):
        lines.append(f"  {i}. {p.name:<25} {p.description}")
    lines.append("")
    return "\n".join(lines)


def format_welcome(persona: Persona) -> str:
    """Format the welcome message after persona selection."""
    lines = [
        "",
        f"── {persona.name} ──",
        "Type your message. Commands: /save, /load, /quit",
        "",
    ]
    return "\n".join(lines)
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_display.py -v`
Expected: 3 passed

**Step 5: Commit**

```bash
git add examples/ai-chatbot/src/chatbot/display.py examples/ai-chatbot/tests/test_display.py
git commit -m "Add terminal display formatting"
```

---

### Task 6: Streaming chat logic

**Files:**
- Create: `examples/ai-chatbot/tests/test_chat.py`
- Create: `examples/ai-chatbot/src/chatbot/chat.py`

**Step 1: Write failing tests**

```python
"""Tests for streaming chat logic."""

import sys
from unittest.mock import MagicMock, patch

import anthropic

from chatbot.chat import create_client, send_message
from chatbot.models import Conversation, Message, Persona


def _make_conversation() -> Conversation:
    return Conversation(
        persona=Persona(name="Test", description="D", system_prompt="Be helpful."),
        messages=[Message(role="user", content="Hello")],
    )


def test_send_message_returns_text():
    """send_message should return the full response text."""
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["Hi ", "there!"])
    mock_stream.get_final_message.return_value = MagicMock(
        content=[MagicMock(type="text", text="Hi there!")]
    )

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    conv = _make_conversation()
    result = send_message(mock_client, conv)
    assert result == "Hi there!"


def test_send_message_uses_system_prompt():
    """send_message should pass the persona's system prompt."""
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["Ok"])
    mock_stream.get_final_message.return_value = MagicMock(
        content=[MagicMock(type="text", text="Ok")]
    )

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    conv = _make_conversation()
    send_message(mock_client, conv)

    call_kwargs = mock_client.messages.stream.call_args[1]
    assert call_kwargs["system"] == "Be helpful."


def test_send_message_uses_correct_model():
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter(["Ok"])
    mock_stream.get_final_message.return_value = MagicMock(
        content=[MagicMock(type="text", text="Ok")]
    )

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    conv = _make_conversation()
    send_message(mock_client, conv)

    call_kwargs = mock_client.messages.stream.call_args[1]
    assert call_kwargs["model"] == "claude-sonnet-4-5"


def test_create_client_fails_without_api_key():
    with patch.dict("os.environ", {}, clear=True):
        # Remove ANTHROPIC_API_KEY if present
        import os
        os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            client = create_client()
            # If we get here, the client was created — that's ok if key exists
        except SystemExit:
            pass  # Expected when no key
```

**Step 2: Run tests to verify they fail**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_chat.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
"""Streaming chat logic using Claude API."""

import sys

import anthropic

from chatbot.models import Conversation

MODEL = "claude-sonnet-4-5"


def create_client() -> anthropic.Anthropic:
    """Create an Anthropic client, exiting if API key is missing."""
    try:
        return anthropic.Anthropic()
    except anthropic.AuthenticationError:
        print("Error: ANTHROPIC_API_KEY not set or invalid.")
        print("  cp .env.example .env  # then add your key")
        sys.exit(1)


def send_message(client: anthropic.Anthropic, conversation: Conversation) -> str:
    """Send the conversation to Claude and stream the response.

    Prints tokens as they arrive. Returns the full response text.
    """
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=conversation.persona.system_prompt,
        messages=conversation.to_api_messages(),
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        final = stream.get_final_message()

    print()  # newline after streaming
    return next(b.text for b in final.content if b.type == "text")
```

**Step 4: Run tests to verify they pass**

Run: `cd examples/ai-chatbot && uv run pytest tests/test_chat.py -v`
Expected: 4 passed

**Step 5: Commit**

```bash
git add examples/ai-chatbot/src/chatbot/chat.py examples/ai-chatbot/tests/test_chat.py
git commit -m "Add streaming chat logic with Claude API"
```

---

### Task 7: CLI runner (run.py)

**Files:**
- Create: `examples/ai-chatbot/run.py`

**Step 1: Write run.py**

```python
#!/usr/bin/env python3
"""AI Chatbot workflow runner.

Pattern: trigger -> ai -> data -> deliver

Interactive terminal chat with streaming responses,
persona presets, and conversation persistence.

Usage:
    uv run python run.py                  # interactive persona selection
    uv run python run.py --persona 1      # select persona by number
"""

import argparse
import os
from pathlib import Path

from chatbot.chat import create_client, send_message
from chatbot.display import format_header, format_persona_menu, format_welcome
from chatbot.memory import list_conversations, load_conversation, save_conversation
from chatbot.models import Conversation, Message
from chatbot.personas import PERSONAS, get_persona

CONVERSATIONS_DIR = Path(__file__).parent / "conversations"


def _load_dotenv():
    """Load .env file if it exists (no external dependency needed)."""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if key and value:
            os.environ.setdefault(key.strip(), value.strip())


def _select_persona() -> int:
    """Interactive persona selection. Returns 0-based index."""
    print(format_header("AI Chatbot — Setup"))
    print(format_persona_menu(PERSONAS))
    choice = input(f"Persona (1-{len(PERSONAS)}): ").strip()
    try:
        return int(choice) - 1
    except ValueError:
        return 0


def _handle_command(command: str, conversation: Conversation) -> bool:
    """Handle a slash command. Returns True if chat should continue."""
    if command == "/quit":
        return False
    if command == "/save":
        path = save_conversation(conversation, CONVERSATIONS_DIR)
        print(f"  Conversation saved to {path}")
        return True
    if command == "/load":
        files = list_conversations(CONVERSATIONS_DIR)
        if not files:
            print("  No saved conversations found.")
            return True
        print("  Saved conversations:")
        for i, f in enumerate(files[:10], 1):
            print(f"    {i}. {f.name}")
        choice = input("  Load (number): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                loaded = load_conversation(files[idx])
                conversation.messages = loaded.messages
                conversation.persona = loaded.persona
                print(f"  Loaded {len(loaded.messages)} messages as {loaded.persona.name}")
        except (ValueError, IndexError):
            print("  Invalid selection.")
        return True
    print(f"  Unknown command: {command}. Available: /save, /load, /quit")
    return True


def main():
    _load_dotenv()

    parser = argparse.ArgumentParser(description="AI Chatbot: trigger -> ai -> data -> deliver")
    parser.add_argument("--persona", type=int, default=None, help="Persona number (1-5, skips interactive selection)")
    args = parser.parse_args()

    # Step 1: Trigger — select persona
    if args.persona is not None:
        persona = get_persona(args.persona - 1)
    else:
        persona = get_persona(_select_persona())

    # Create conversation and client
    conversation = Conversation(persona=persona, messages=[])
    client = create_client()

    print(format_welcome(persona))

    # Step 2-4: Chat loop (ai -> data -> deliver)
    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                if not _handle_command(user_input, conversation):
                    break
                continue

            # AI — send to Claude with streaming
            conversation.messages.append(Message(role="user", content=user_input))
            print("Assistant: ", end="", flush=True)
            response_text = send_message(client, conversation)
            conversation.messages.append(Message(role="assistant", content=response_text))
            print()

    except KeyboardInterrupt:
        print("\n")

    # Auto-save on exit if there are messages
    if conversation.messages:
        path = save_conversation(conversation, CONVERSATIONS_DIR)
        print(f"Conversation auto-saved to {path}")


if __name__ == "__main__":
    main()
```

**Step 2: Verify all tests pass**

Run: `cd examples/ai-chatbot && uv run pytest -v`
Expected: All tests pass (models: 4, personas: 6, memory: 5, display: 3, chat: 4 = ~22 total)

**Step 3: Commit**

```bash
git add examples/ai-chatbot/run.py
git commit -m "Add CLI runner with interactive chat loop"
```

---

### Task 8: Integration — update README and website

**Files:**
- Modify: `README.md`
- Modify: `scripts/generate_site.py`

**Step 1: Update README.md**

In the "Runnable Examples" table, add the chatbot row:

```markdown
| [AI Chatbot](examples/ai-chatbot/) | `trigger -> ai -> data -> deliver` | Streaming terminal chat with 5 persona presets and conversation persistence |
```

Update the "More examples coming" line to remove "AI Chatbot" from the list.

Update test count to reflect new total.

Update Project Structure to include `ai-chatbot/`.

**Step 2: Update generate_site.py**

Add `example` field to the "AI Chatbot / Assistant" entry in WIZARD_DATA:

```python
"example": {
    "path": "examples/ai-chatbot",
    "label": "Runnable Example",
    "desc": "~22 tests, Claude API streaming, 5 personas, conversation memory — ready to run",
},
```

**Step 3: Regenerate site**

Run: `uv run python scripts/generate_site.py`

**Step 4: Run all tests (root + both examples)**

Run: `uv run pytest -v` (from root)
Run: `cd examples/ai-chatbot && uv run pytest -v`
Run: `cd examples/ai-content-creation && uv run pytest -v`

**Step 5: Commit**

```bash
git add README.md scripts/generate_site.py docs/index.html
git commit -m "Link AI Chatbot example from README and website"
```

---

### Task 9: Live test and push

**Step 1: Copy .env to ai-chatbot**

```bash
cp examples/ai-content-creation/.env examples/ai-chatbot/.env
```

**Step 2: Run the chatbot with real API**

```bash
cd examples/ai-chatbot && uv run python run.py --persona 3
```

Test: send 2-3 messages, try `/save`, try `/quit`, verify auto-save.

**Step 3: Push**

```bash
git push
```
