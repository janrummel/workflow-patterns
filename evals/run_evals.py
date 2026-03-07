"""Evaluation suite for the workflow patterns system.

Runs predefined test cases against the MCP server tools and reports
how well the system detects categories, matches patterns, and generates
correct implementation suggestions.

Usage:
    uv run python evals/run_evals.py
"""

import json
from pathlib import Path

from workflow_patterns.mcp_server.server import search_patterns, suggest_implementation


def load_test_cases() -> list[dict]:
    path = Path(__file__).parent / "test_cases.json"
    with open(path) as f:
        return json.load(f)


def eval_search(case: dict) -> tuple[bool, str]:
    """Evaluate a search_patterns test case."""
    result = search_patterns(case["query"])

    # Check if expected categories were detected
    for cat in case["expected_categories"]:
        if cat not in result:
            return False, f"Category '{cat}' not found in result"

    # Check if result contains expected pattern elements
    for element in case.get("expected_pattern_contains", []):
        if element not in result:
            return False, f"Pattern element '{element}' not found in result"

    return True, "OK"


def eval_implementation(case: dict) -> tuple[bool, str]:
    """Evaluate a suggest_implementation test case."""
    result = suggest_implementation(case["query_pattern"])

    # Check expected components
    for comp in case.get("expected_components", []):
        if comp.lower() not in result.lower():
            return False, f"Component '{comp}' not found in result"

    # Check complexity
    expected = case.get("expected_complexity")
    if expected and f"Complexity: {expected}" not in result:
        return False, f"Expected complexity '{expected}', not found"

    return True, "OK"


def main():
    cases = load_test_cases()
    passed = 0
    failed = 0
    results = []

    print("=" * 60)
    print("WORKFLOW PATTERNS — EVALUATION SUITE")
    print("=" * 60)
    print()

    for case in cases:
        case_id = case["id"]
        desc = case["description"]

        if "query_pattern" in case:
            success, message = eval_implementation(case)
        else:
            success, message = eval_search(case)

        status = "PASS" if success else "FAIL"
        if success:
            passed += 1
        else:
            failed += 1

        results.append({"id": case_id, "status": status, "message": message})
        icon = "+" if success else "-"
        print(f"  [{icon}] {case_id}: {desc}")
        if not success:
            print(f"      Reason: {message}")

    print()
    print("-" * 60)
    print(f"Results: {passed}/{passed + failed} passed ({passed / (passed + failed) * 100:.0f}%)")
    if failed > 0:
        print(f"         {failed} failed")
    print("-" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    raise SystemExit(0 if success else 1)
