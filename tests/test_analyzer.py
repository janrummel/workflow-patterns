"""Tests for the pattern analyzer."""

from pathlib import Path

from workflow_patterns.parser.parse import parse_directory
from workflow_patterns.patterns.analyzer import (
    extract_common_pairs,
    extract_node_stats,
    extract_patterns,
    find_similar_workflows,
)

SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample_workflows"


def _load_workflows():
    if not SAMPLE_DIR.exists():
        return None
    return parse_directory(SAMPLE_DIR)


def test_extract_patterns_returns_results():
    workflows = _load_workflows()
    if not workflows:
        return
    patterns = extract_patterns(workflows)
    assert len(patterns) > 0
    for p in patterns:
        assert p.signature
        assert p.count >= 1
        assert len(p.workflows) == p.count


def test_simplified_patterns_are_shorter():
    workflows = _load_workflows()
    if not workflows:
        return
    # Simplified signatures should be <= length of full signatures
    for wf in workflows:
        assert len(wf.simple_signature) <= len(wf.pattern_signature)


def test_node_stats_covers_all_categories():
    workflows = _load_workflows()
    if not workflows:
        return
    stats = extract_node_stats(workflows)
    assert "ai" in stats
    assert "trigger" in stats
    assert "skip" not in stats  # skip nodes should be filtered by parser


def test_common_pairs_are_sorted():
    workflows = _load_workflows()
    if not workflows:
        return
    pairs = extract_common_pairs(workflows)
    assert len(pairs) > 0
    # Should be sorted by count descending
    counts = [c for _, _, c in pairs]
    assert counts == sorted(counts, reverse=True)


def test_find_similar_workflows():
    workflows = _load_workflows()
    if not workflows:
        return
    results = find_similar_workflows(["trigger", "ai", "deliver"], workflows, top_n=3)
    assert len(results) <= 3
    # Scores should be between 0 and 1
    for wf, score in results:
        assert 0.0 <= score <= 1.0
    # Should be sorted by score descending
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)
