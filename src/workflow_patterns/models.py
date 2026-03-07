"""Data models for workflow patterns.

A workflow is a directed graph of nodes connected by edges.
Each node has a type and a category (trigger, action, transform, ai, etc.).
A pattern is an abstracted sequence of categories that appears across many workflows.
"""

from dataclasses import dataclass, field


# --- Node category mapping ---
# Maps n8n node type prefixes to abstract categories
NODE_CATEGORIES = {
    # Triggers — what starts a workflow
    "Trigger": "trigger",
    "trigger": "trigger",
    "webhook": "trigger",
    "schedule": "trigger",
    "cron": "trigger",
    # AI / LLM
    "langchain": "ai",
    "openAi": "ai",
    "anthropic": "ai",
    # Data sources
    "googleSheets": "data",
    "postgres": "data",
    "mysql": "data",
    "mongo": "data",
    "airtable": "data",
    "nocodb": "data",
    "supabase": "data",
    # Communication / Delivery
    "gmail": "deliver",
    "slack": "deliver",
    "telegram": "deliver",
    "discord": "deliver",
    "email": "deliver",
    # Transform / Logic
    "set": "transform",
    "code": "transform",
    "function": "transform",
    "if": "logic",
    "switch": "logic",
    "merge": "logic",
    "splitInBatches": "logic",
    # HTTP / API
    "httpRequest": "api",
    "http": "api",
    # Storage
    "googleDrive": "storage",
    "s3": "storage",
    "ftp": "storage",
}

# Nodes to skip (not meaningful for pattern analysis)
SKIP_NODES = {"stickyNote", "noOp", "start"}


@dataclass
class Node:
    """A single node in a workflow."""

    name: str
    node_type: str  # e.g. "n8n-nodes-base.gmail"
    category: str  # e.g. "deliver"

    @property
    def type_short(self) -> str:
        """Short type name without prefix. e.g. 'gmail' from 'n8n-nodes-base.gmail'."""
        return self.node_type.split(".")[-1]


@dataclass
class Edge:
    """A connection between two nodes."""

    source: str  # node name
    target: str  # node name


@dataclass
class Workflow:
    """A parsed workflow with nodes and edges."""

    name: str
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)  # from metadata
    author: str = ""
    source_url: str = ""

    @property
    def node_categories(self) -> list[str]:
        """List of unique node categories in this workflow."""
        return sorted(set(n.category for n in self.nodes))

    @property
    def pattern_signature(self) -> str:
        """Abstract pattern as a string like 'trigger -> transform -> ai -> deliver'."""
        # Walk the graph from trigger nodes to build the pattern
        if not self.edges:
            return " -> ".join(n.category for n in self.nodes)

        # Build adjacency list
        adj: dict[str, list[str]] = {}
        for edge in self.edges:
            adj.setdefault(edge.source, []).append(edge.target)

        # Find starting nodes (triggers or nodes with no incoming edges)
        targets = {e.target for e in self.edges}
        sources = {e.source for e in self.edges}
        start_nodes = [n for n in self.nodes if n.name in (sources - targets)]
        if not start_nodes:
            start_nodes = [n for n in self.nodes if n.category == "trigger"]
        if not start_nodes and self.nodes:
            start_nodes = [self.nodes[0]]

        # BFS to build ordered category chain
        visited: set[str] = set()
        category_order: list[str] = []
        queue = [n.name for n in start_nodes]

        node_map = {n.name: n for n in self.nodes}
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            if current in node_map:
                cat = node_map[current].category
                if not category_order or category_order[-1] != cat:
                    category_order.append(cat)
            for neighbor in adj.get(current, []):
                queue.append(neighbor)

        return " -> ".join(category_order) if category_order else "unknown"

    @property
    def simple_signature(self) -> str:
        """Simplified pattern — unique categories in order of first appearance.

        e.g. 'trigger -> ai -> transform -> deliver'
        (no repeated categories, captures the essence of the workflow)
        """
        full = self.pattern_signature
        seen: set[str] = set()
        simple: list[str] = []
        for step in full.split(" -> "):
            if step not in seen:
                seen.add(step)
                simple.append(step)
        return " -> ".join(simple)


@dataclass
class Pattern:
    """An abstracted automation pattern found across multiple workflows."""

    signature: str  # e.g. "trigger -> transform -> ai -> deliver"
    workflows: list[str] = field(default_factory=list)  # workflow names
    count: int = 0
    example_nodes: list[str] = field(default_factory=list)  # concrete node types

    @property
    def steps(self) -> list[str]:
        """Individual steps in the pattern."""
        return [s.strip() for s in self.signature.split("->")]


def categorize_node(node_type: str) -> str:
    """Map an n8n node type to an abstract category."""
    short = node_type.split(".")[-1]

    # Check if it should be skipped
    for skip in SKIP_NODES:
        if skip.lower() in short.lower():
            return "skip"

    # Check against known categories
    for keyword, category in NODE_CATEGORIES.items():
        if keyword.lower() in short.lower() or keyword.lower() in node_type.lower():
            return category

    return "other"
