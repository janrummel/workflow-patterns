"""Terminal display formatting for the API Integration workflow."""

from api_workflow.models import Integration


def format_header(title: str) -> str:
    """Create a boxed ASCII header."""
    width = max(len(title) + 8, 42)
    top = "╔" + "═" * width + "╗"
    mid = "║" + title.center(width) + "║"
    bot = "╚" + "═" * width + "╝"
    return f"\n{top}\n{mid}\n{bot}\n"


def format_integration_menu(integrations: list[Integration]) -> str:
    """Format integration selection menu."""
    lines = []
    for i, integ in enumerate(integrations, 1):
        lines.append(f"  {i}. {integ.name:<22s} {integ.description}")
    return "\n".join(lines)


def format_records_table(records: list[dict], max_rows: int = 15) -> str:
    """Format records as an ASCII table."""
    if not records:
        return "(no records)"

    headers = list(records[0].keys())
    widths = {h: len(h) for h in headers}
    display = records[:max_rows]
    for rec in display:
        for h in headers:
            widths[h] = max(widths[h], len(str(rec.get(h, ""))))

    def row_str(values: dict) -> str:
        cells = [str(values.get(h, "")).ljust(widths[h]) for h in headers]
        return "│ " + " │ ".join(cells) + " │"

    sep_top = "┌─" + "─┬─".join("─" * widths[h] for h in headers) + "─┐"
    sep_mid = "├─" + "─┼─".join("─" * widths[h] for h in headers) + "─┤"
    sep_bot = "└─" + "─┴─".join("─" * widths[h] for h in headers) + "─┘"

    header_vals = {h: h for h in headers}
    lines = [sep_top, row_str(header_vals), sep_mid]
    for rec in display:
        lines.append(row_str(rec))
    lines.append(sep_bot)

    if len(records) > max_rows:
        lines.append(f"... and {len(records) - max_rows} more rows")

    return "\n".join(lines)
