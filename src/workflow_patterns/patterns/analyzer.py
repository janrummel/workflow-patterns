"""Pattern analyzer — finds recurring patterns across workflows.

Takes a list of parsed workflows, extracts their pattern signatures,
groups similar ones, and ranks them by frequency.
"""

from collections import Counter

from workflow_patterns.models import Pattern, Workflow


def extract_patterns(workflows: list[Workflow], simplified: bool = True) -> list[Pattern]:
    """Extract and rank patterns from a list of workflows.

    Groups workflows by their pattern signature and returns
    patterns sorted by frequency (most common first).

    Args:
        simplified: Use simplified signatures (unique categories only).
                    This produces more matches across workflows.
    """
    # Group workflows by pattern signature
    signature_groups: dict[str, list[Workflow]] = {}
    for wf in workflows:
        sig = wf.simple_signature if simplified else wf.pattern_signature
        signature_groups.setdefault(sig, []).append(wf)

    # Build Pattern objects
    patterns = []
    for sig, wfs in signature_groups.items():
        # Collect example node types from the first workflow
        example_nodes = [n.type_short for n in wfs[0].nodes]

        patterns.append(Pattern(
            signature=sig,
            workflows=[wf.name for wf in wfs],
            count=len(wfs),
            example_nodes=example_nodes,
        ))

    # Sort by frequency
    return sorted(patterns, key=lambda p: p.count, reverse=True)


def extract_node_stats(workflows: list[Workflow]) -> dict[str, int]:
    """Count how often each node category appears across all workflows."""
    counter: Counter[str] = Counter()
    for wf in workflows:
        for node in wf.nodes:
            counter[node.category] += 1
    return dict(counter.most_common())


def extract_common_pairs(workflows: list[Workflow]) -> list[tuple[str, str, int]]:
    """Find the most common category-to-category connections.

    Returns list of (source_category, target_category, count) sorted by count.
    """
    pair_counter: Counter[tuple[str, str]] = Counter()
    for wf in workflows:
        node_map = {n.name: n for n in wf.nodes}
        for edge in wf.edges:
            src = node_map.get(edge.source)
            tgt = node_map.get(edge.target)
            if src and tgt:
                pair_counter[(src.category, tgt.category)] += 1

    return [(s, t, c) for (s, t), c in pair_counter.most_common()]


def find_similar_workflows(
    query_categories: list[str], workflows: list[Workflow], top_n: int = 5
) -> list[tuple[Workflow, float]]:
    """Find workflows that use similar node categories.

    Uses Jaccard similarity between the query categories and each workflow's categories.
    Returns list of (workflow, similarity_score) sorted by score.
    """
    query_set = set(query_categories)
    results = []

    for wf in workflows:
        wf_set = set(wf.node_categories)
        if not query_set or not wf_set:
            continue
        # Jaccard similarity
        intersection = len(query_set & wf_set)
        union = len(query_set | wf_set)
        score = intersection / union if union > 0 else 0.0
        results.append((wf, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]
