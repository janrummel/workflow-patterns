"""Summarize step (ai): use Claude API to summarize articles."""

import sys

import anthropic

from content_workflow.models import Article, Summary

MODEL = "claude-sonnet-4-5"


def summarize_articles(articles: list[Article]) -> list[Summary]:
    """Summarize each article using Claude API."""
    try:
        client = anthropic.Anthropic()
    except anthropic.AuthenticationError:
        print("Error: ANTHROPIC_API_KEY not set or invalid.")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    summaries = []
    for article in articles:
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"Summarize this article in 2-3 sentences:\n\nTitle: {article.title}\n\n{article.content}",
            }],
        )
        text = next(b.text for b in response.content if b.type == "text")
        summaries.append(Summary(title=article.title, summary_text=text, original_url=article.url))
    return summaries
