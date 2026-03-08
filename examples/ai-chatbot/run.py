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
