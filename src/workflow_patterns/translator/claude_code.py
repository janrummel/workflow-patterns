"""Translator — maps abstract workflow patterns to Claude Code architectures.

Takes a pattern signature (e.g. 'trigger -> ai -> transform -> deliver')
and recommends how to implement it with Claude Code components:
MCP servers, skills, sub-agents, cron jobs, etc.
"""

from dataclasses import dataclass, field


@dataclass
class ClaudeCodeComponent:
    """A single building block in a Claude Code architecture."""

    name: str
    component_type: str  # "mcp_server", "skill", "sub_agent", "cron", "script"
    description: str
    example: str = ""


@dataclass
class ClaudeCodeArchitecture:
    """A recommended Claude Code implementation for a workflow pattern."""

    pattern: str  # the original pattern signature
    summary: str  # one-line description of what this achieves
    components: list[ClaudeCodeComponent] = field(default_factory=list)
    implementation_steps: list[str] = field(default_factory=list)
    complexity: str = "low"  # low, medium, high

    def to_text(self) -> str:
        """Render as readable text."""
        lines = [
            f"## Pattern: {self.pattern}",
            f"**{self.summary}**",
            f"Complexity: {self.complexity}",
            "",
            "### Components needed:",
        ]
        for comp in self.components:
            lines.append(f"- **{comp.name}** ({comp.component_type}): {comp.description}")
            if comp.example:
                lines.append(f"  Example: `{comp.example}`")
        lines.append("")
        lines.append("### Implementation steps:")
        for i, step in enumerate(self.implementation_steps, 1):
            lines.append(f"{i}. {step}")
        return "\n".join(lines)


# --- Category to Claude Code component mappings ---

CATEGORY_COMPONENTS: dict[str, ClaudeCodeComponent] = {
    "trigger": ClaudeCodeComponent(
        name="Trigger / Scheduler",
        component_type="cron",
        description="Starts the workflow on a schedule or event",
        example="crontab, launchd, or a file watcher script",
    ),
    "ai": ClaudeCodeComponent(
        name="Claude Agent",
        component_type="sub_agent",
        description="Processes, analyzes, or generates content using Claude",
        example="claude --prompt 'Analyze this data and summarize key findings'",
    ),
    "transform": ClaudeCodeComponent(
        name="Data Transformer",
        component_type="script",
        description="Reshapes, filters, or enriches data between steps",
        example="Python script that parses JSON, extracts fields, formats output",
    ),
    "deliver": ClaudeCodeComponent(
        name="Output Delivery",
        component_type="mcp_server",
        description="Sends results to a destination (email, Slack, file)",
        example="MCP server with send_email() or post_to_slack() tools",
    ),
    "data": ClaudeCodeComponent(
        name="Data Source",
        component_type="mcp_server",
        description="Reads from or writes to a database or spreadsheet",
        example="MCP server with query_database() or read_spreadsheet() tools",
    ),
    "api": ClaudeCodeComponent(
        name="External API Client",
        component_type="mcp_server",
        description="Calls external APIs to fetch or push data",
        example="MCP server with fetch_url() or call_api() tools",
    ),
    "logic": ClaudeCodeComponent(
        name="Control Flow",
        component_type="skill",
        description="Branching, conditions, or loops in the workflow",
        example="Claude skill that decides next action based on conditions",
    ),
    "storage": ClaudeCodeComponent(
        name="File Storage",
        component_type="mcp_server",
        description="Reads from or writes to file storage (Drive, S3, local)",
        example="MCP server with read_file() or upload_file() tools",
    ),
    "other": ClaudeCodeComponent(
        name="Custom Integration",
        component_type="script",
        description="A specialized step — may need a custom script or tool",
        example="Python script tailored to the specific service",
    ),
}

# Complexity rules based on number of distinct categories
COMPLEXITY_THRESHOLDS = {
    2: "low",       # e.g. trigger -> deliver
    4: "medium",    # e.g. trigger -> ai -> transform -> deliver
    99: "high",     # 5+ categories
}


def translate_pattern(pattern_signature: str) -> ClaudeCodeArchitecture:
    """Translate an abstract pattern signature into a Claude Code architecture.

    Args:
        pattern_signature: e.g. 'trigger -> ai -> transform -> deliver'

    Returns:
        A ClaudeCodeArchitecture with components and implementation steps.
    """
    steps = [s.strip() for s in pattern_signature.split("->")]

    # Map each step to a component
    components = []
    seen_types: set[str] = set()
    for step in steps:
        comp = CATEGORY_COMPONENTS.get(step)
        if comp and step not in seen_types:
            components.append(comp)
            seen_types.add(step)

    # Determine complexity
    n_categories = len(seen_types)
    complexity = "high"
    for threshold, level in sorted(COMPLEXITY_THRESHOLDS.items()):
        if n_categories <= threshold:
            complexity = level
            break

    # Generate summary
    summary = _generate_summary(steps)

    # Generate implementation steps
    impl_steps = _generate_implementation_steps(components)

    return ClaudeCodeArchitecture(
        pattern=pattern_signature,
        summary=summary,
        components=components,
        implementation_steps=impl_steps,
        complexity=complexity,
    )


def _generate_summary(steps: list[str]) -> str:
    """Generate a human-readable summary from pattern steps."""
    step_descriptions = {
        "trigger": "triggered by an event or schedule",
        "ai": "processed by Claude",
        "transform": "data is transformed",
        "deliver": "results are delivered",
        "data": "data is read/written from a source",
        "api": "an external API is called",
        "logic": "conditional logic is applied",
        "storage": "files are stored or retrieved",
        "other": "a custom step is performed",
    }

    parts = []
    for step in steps:
        desc = step_descriptions.get(step)
        if desc and desc not in parts:
            parts.append(desc)

    if not parts:
        return "A workflow pattern"

    # Capitalize first part, join with commas and 'then'
    result = parts[0].capitalize()
    if len(parts) > 1:
        result += ", then " + ", then ".join(parts[1:])
    return result + "."


def _generate_implementation_steps(components: list[ClaudeCodeComponent]) -> list[str]:
    """Generate ordered implementation steps based on components."""
    impl_steps = []

    # Group by type
    mcp_servers = [c for c in components if c.component_type == "mcp_server"]
    scripts = [c for c in components if c.component_type == "script"]
    agents = [c for c in components if c.component_type == "sub_agent"]
    crons = [c for c in components if c.component_type == "cron"]
    skills = [c for c in components if c.component_type == "skill"]

    if mcp_servers:
        names = ", ".join(c.name for c in mcp_servers)
        impl_steps.append(f"Build MCP server(s) for: {names}")
        impl_steps.append("Define tools with clear input/output schemas")

    if scripts:
        names = ", ".join(c.name for c in scripts)
        impl_steps.append(f"Write Python scripts for: {names}")

    if agents:
        impl_steps.append("Configure Claude agent with access to the MCP server tools")
        impl_steps.append("Write a CLAUDE.md that defines the agent's behavior and available skills")

    if skills:
        names = ", ".join(c.name for c in skills)
        impl_steps.append(f"Create Claude skills for: {names}")

    if crons:
        impl_steps.append("Set up a scheduler (cron/launchd) to trigger the workflow")

    impl_steps.append("Write tests for each component")
    impl_steps.append("Write evals to verify the agent produces correct outputs")

    return impl_steps
