"""Tests for the n8n workflow parser."""

from pathlib import Path

from workflow_patterns.models import categorize_node
from workflow_patterns.parser.parse import parse_directory


SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample_workflows"


def test_categorize_known_nodes():
    assert categorize_node("n8n-nodes-base.gmail") == "deliver"
    assert categorize_node("n8n-nodes-base.googleSheetsTrigger") == "trigger"
    assert categorize_node("@n8n/n8n-nodes-langchain.chainLlm") == "ai"
    assert categorize_node("n8n-nodes-base.httpRequest") == "api"
    assert categorize_node("n8n-nodes-base.set") == "transform"


def test_categorize_skip_nodes():
    assert categorize_node("n8n-nodes-base.stickyNote") == "skip"
    assert categorize_node("n8n-nodes-base.noOp") == "skip"


def test_parse_directory():
    if not SAMPLE_DIR.exists():
        return  # skip if no sample data
    workflows = parse_directory(SAMPLE_DIR)
    assert len(workflows) > 0
    for wf in workflows:
        assert wf.name
        assert len(wf.nodes) > 0


def test_workflow_has_pattern():
    if not SAMPLE_DIR.exists():
        return
    workflows = parse_directory(SAMPLE_DIR)
    for wf in workflows:
        sig = wf.pattern_signature
        assert sig  # not empty
        assert "skip" not in sig  # skip nodes should be filtered
