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
