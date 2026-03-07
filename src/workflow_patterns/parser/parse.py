"""Parser for n8n workflow JSON files.

Reads workflow.json and optional metadata.json, returns a Workflow object.
"""

import json
from pathlib import Path

from workflow_patterns.models import Edge, Node, Workflow, categorize_node


def parse_workflow(workflow_path: Path, metadata_path: Path | None = None) -> Workflow:
    """Parse a single n8n workflow JSON into a Workflow object.

    Args:
        workflow_path: Path to workflow.json
        metadata_path: Optional path to metadata.json
    """
    with open(workflow_path, encoding="utf-8") as f:
        data = json.load(f)

    # Parse nodes (skip sticky notes and noOps)
    nodes = []
    for raw_node in data.get("nodes", []):
        node_type = raw_node.get("type", "")
        category = categorize_node(node_type)
        if category == "skip":
            continue
        nodes.append(Node(
            name=raw_node.get("name", "unknown"),
            node_type=node_type,
            category=category,
        ))

    # Parse connections (handles inconsistent n8n JSON formats)
    edges = []
    connections = data.get("connections", {})
    if isinstance(connections, dict):
        for source_name, conn_data in connections.items():
            if not isinstance(conn_data, dict):
                continue
            for conn_type_data in conn_data.values():
                if not isinstance(conn_type_data, list):
                    continue
                for connection_list in conn_type_data:
                    if not isinstance(connection_list, list):
                        continue
                    for conn in connection_list:
                        if not isinstance(conn, dict):
                            continue
                        target_name = conn.get("node", "")
                        if target_name:
                            edges.append(Edge(source=source_name, target=target_name))

    # Parse metadata if available
    author = ""
    categories = []
    source_url = ""
    if metadata_path and metadata_path.exists():
        with open(metadata_path, encoding="utf-8") as f:
            meta = json.load(f)
        author = meta.get("user_name", "")
        source_url = meta.get("url_n8n", "")
        categories = [c.get("name", "") for c in meta.get("categories", [])]

    return Workflow(
        name=data.get("name", workflow_path.parent.name),
        nodes=nodes,
        edges=edges,
        categories=categories,
        author=author,
        source_url=source_url,
    )


def parse_directory(data_dir: Path) -> list[Workflow]:
    """Parse all workflow folders in a directory.

    Expects structure: data_dir/<workflow_name>/workflow.json
    """
    workflows = []
    for folder in sorted(data_dir.iterdir()):
        if not folder.is_dir():
            continue

        # Find workflow JSON (not metadata)
        workflow_files = [f for f in folder.glob("*.json") if "metada" not in f.name]
        metadata_files = list(folder.glob("metada*.json"))

        if not workflow_files:
            continue

        workflow_path = workflow_files[0]
        metadata_path = metadata_files[0] if metadata_files else None

        try:
            wf = parse_workflow(workflow_path, metadata_path)
            workflows.append(wf)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse {folder.name}: {e}")
            continue

    return workflows
