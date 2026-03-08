# AI Chatbot Example — Design

**Date:** 2026-03-08
**Pattern:** `trigger → ai → data → deliver`
**Status:** Approved

## Goal

Second runnable example for workflow-patterns. A terminal-based chat with streaming responses, persona presets, and conversation persistence. Complements the AI Content Creation example by demonstrating different Claude API features (streaming, multi-turn).

## Architecture

```
select_persona() → stream_chat() → save_conversation() → terminal output
trigger            ai               data                  deliver
```

## Module Structure

```
examples/ai-chatbot/
├── run.py                      # CLI entry point
├── .env.example                # ANTHROPIC_API_KEY template
├── .gitignore                  # .env, __pycache__, conversations/
├── pyproject.toml              # anthropic as only runtime dependency
├── src/chatbot/
│   ├── __init__.py
│   ├── models.py               # Dataclasses: Persona, Message, Conversation
│   ├── personas.py             # 5 persona presets with system prompts
│   ├── chat.py                 # Streaming chat (client.messages.stream)
│   ├── memory.py               # Conversation save/load (JSON)
│   └── display.py              # Terminal formatting (streaming output)
├── tests/
│   ├── test_personas.py
│   ├── test_chat.py
│   ├── test_memory.py
│   └── test_display.py
└── conversations/              # Saved conversations (gitignored)
```

## Modules

### personas.py
5 curated persona presets, each with a tailored system prompt:

| Persona | Focus |
|---------|-------|
| Code Reviewer | Code quality, security, best practices |
| Writing Coach | Clarity, structure, tone |
| Research Assistant | Facts, sources, systematic analysis |
| Explain Like I'm 5 | Complex topics made simple |
| Debate Partner | Counterarguments, find weaknesses |

Interactive selection menu (like content-creation presets). Also available via `--persona` flag.

### chat.py
- `client.messages.stream()` with `text_stream` for live token output
- Full conversation history sent each turn
- Configurable max_tokens
- Clean exit handling (`/quit`, `/save`, Ctrl+C)

### memory.py
- `save_conversation(conv, path)` → JSON with metadata (persona, timestamp, messages)
- `load_conversation(path)` → restore a previous session
- `list_conversations(dir)` → show saved sessions
- Exposed via `/save` and `/load` chat commands

### display.py
- Stream tokens with `flush=True`
- Role labels (You / Assistant)
- Persona name in prompt header

### models.py
```python
@dataclass
class Persona:
    name: str
    description: str
    system_prompt: str

@dataclass
class Message:
    role: str       # "user" or "assistant"
    content: str

@dataclass
class Conversation:
    persona: Persona
    messages: list[Message]
    started_at: datetime
```

## UX Flow

```
$ uv run python run.py

╔══════════════════════════════════════════╗
║         AI Chatbot — Setup              ║
╚══════════════════════════════════════════╝

Choose a persona:
  1. Code Reviewer       Code quality, security, best practices
  2. Writing Coach       Clarity, structure, tone
  3. Research Assistant   Facts, sources, systematic analysis
  4. Explain Like I'm 5  Complex topics made simple
  5. Debate Partner       Counterarguments, find weaknesses

Persona (1-5): 3

── Research Assistant ──
Type your message. Commands: /save, /load, /quit

You: What are the main approaches to AI alignment?
Assistant: [streams token by token...]

You: /save
Conversation saved to conversations/2026-03-08_research-assistant.json

You: /quit
```

## Key Differences from Content-Creation Example

| Aspect | Content Creation | Chatbot |
|--------|-----------------|---------|
| API style | `messages.create()` (batch) | `messages.stream()` (streaming) |
| Interaction | One-shot run | Interactive loop |
| Pattern | `api → ai → transform → deliver` | `trigger → ai → data → deliver` |
| Data flow | Feeds → summaries → file | User input → conversation → JSON |
| Presets | 60 feed sources | 5 personas |

## Dependencies

- `anthropic` (runtime)
- `pytest` (dev)
- No other dependencies

## Testing Strategy

- Mock `client.messages.stream()` for chat tests
- Real dataclass tests for models
- File I/O tests for memory (tmp_path)
- Pure function tests for display formatting
- Target: ~20-25 tests
