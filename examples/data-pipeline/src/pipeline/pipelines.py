"""Pipeline presets for the Data Pipeline workflow."""

from pipeline.models import Pipeline, TransformStep

PIPELINES: list[Pipeline] = [
    Pipeline(
        name="Sales Summary",
        description="Filter by region, aggregate revenue by product",
        steps=[
            TransformStep(
                name="filter_region",
                description="Keep EMEA records only",
                operation="filter",
                params={"column": "region", "operator": "eq", "value": "EMEA"},
            ),
            TransformStep(
                name="aggregate_revenue",
                description="Sum revenue by product",
                operation="aggregate",
                params={"group_by": "product", "agg_column": "revenue", "operation": "sum"},
            ),
            TransformStep(
                name="sort_revenue",
                description="Sort by revenue descending",
                operation="sort",
                params={"column": "revenue", "ascending": False, "numeric": True},
            ),
        ],
    ),
    Pipeline(
        name="Top Performers",
        description="Sort by revenue, show top results",
        steps=[
            TransformStep(
                name="sort_by_revenue",
                description="Sort by revenue descending",
                operation="sort",
                params={"column": "revenue", "ascending": False, "numeric": True},
            ),
        ],
    ),
    Pipeline(
        name="Data Cleanup",
        description="Deduplicate and normalize data",
        steps=[
            TransformStep(
                name="deduplicate",
                description="Remove duplicate entries",
                operation="deduplicate",
                params={"columns": ["date", "region", "product"]},
            ),
            TransformStep(
                name="sort_clean",
                description="Sort by date",
                operation="sort",
                params={"column": "date", "ascending": True},
            ),
        ],
    ),
    Pipeline(
        name="Period Comparison",
        description="Filter by date range for period analysis",
        steps=[
            TransformStep(
                name="filter_q1",
                description="Keep Q1 data (Jan-Mar)",
                operation="filter",
                params={"column": "date", "operator": "lt", "value": "2026-04"},
            ),
            TransformStep(
                name="aggregate_by_region",
                description="Sum revenue by region",
                operation="aggregate",
                params={"group_by": "region", "agg_column": "revenue", "operation": "sum"},
            ),
            TransformStep(
                name="sort_regions",
                description="Sort by revenue descending",
                operation="sort",
                params={"column": "revenue", "ascending": False, "numeric": True},
            ),
        ],
    ),
    Pipeline(
        name="Custom Report",
        description="Computed columns, rename headers, export",
        steps=[
            TransformStep(
                name="add_unit_price",
                description="Calculate revenue per unit",
                operation="add_column",
                params={"name": "label", "expr_cols": ["product", "region"], "expr_op": "concat", "separator": " - "},
            ),
            TransformStep(
                name="rename_headers",
                description="Rename columns for report",
                operation="rename",
                params={"mapping": {"revenue": "total_revenue", "units": "quantity"}},
            ),
            TransformStep(
                name="sort_report",
                description="Sort by total revenue",
                operation="sort",
                params={"column": "total_revenue", "ascending": False, "numeric": True},
            ),
        ],
    ),
]


def get_pipeline(index: int) -> Pipeline:
    """Get pipeline by index, clamping to valid range."""
    clamped = max(0, min(index, len(PIPELINES) - 1))
    return PIPELINES[clamped]
