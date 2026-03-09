"""Terminal display formatting for the Data Pipeline workflow."""

from pipeline.models import Dataset, Pipeline


def format_header(title: str) -> str:
    """Create a boxed ASCII header."""
    width = max(len(title) + 8, 42)
    top = "╔" + "═" * width + "╗"
    mid = "║" + title.center(width) + "║"
    bot = "╚" + "═" * width + "╝"
    return f"\n{top}\n{mid}\n{bot}\n"


def format_pipeline_menu(pipelines: list[Pipeline]) -> str:
    """Format pipeline selection menu."""
    lines = []
    for i, p in enumerate(pipelines, 1):
        lines.append(f"  {i}. {p.name:<22s} {p.description}")
    return "\n".join(lines)


def format_stats(dataset: Dataset) -> str:
    """Format dataset statistics."""
    return f"  {dataset.row_count} records, {len(dataset.headers)} columns"
