# Data Pipeline Example — Design

**Date:** 2026-03-08
**Pattern:** `trigger → data → transform → data`
**Status:** Approved

## Goal

Fifth runnable example for workflow-patterns. A data processing pipeline that reads structured data, applies transformations (filtering, aggregation, enrichment), and writes results. Demonstrates the `data → transform → data` pattern — read, process, write.

## Architecture

```
select_pipeline() → load_data() → transform_data() → save_results()
trigger              data          transform           data
```

## Module Structure

```
examples/data-pipeline/
├── run.py                      # CLI entry point
├── .env.example                # No config needed
├── .gitignore                  # .env, __pycache__, output/
├── pyproject.toml              # Zero runtime dependencies (stdlib only)
├── src/pipeline/
│   ├── __init__.py
│   ├── models.py               # Dataclasses: Record, Dataset, Pipeline, TransformResult
│   ├── pipelines.py            # 5 pipeline presets
│   ├── reader.py               # Load data from CSV/JSON (data read layer)
│   ├── transforms.py           # Transform functions (filter, aggregate, enrich)
│   ├── writer.py               # Save results to CSV/JSON (data write layer)
│   └── display.py              # Terminal formatting
├── tests/
│   ├── test_models.py
│   ├── test_pipelines.py
│   ├── test_reader.py
│   ├── test_transforms.py
│   ├── test_writer.py
│   ├── test_display.py
│   └── __init__.py
├── data/                       # Sample input data (CSV)
│   └── sales_data.csv
└── output/                     # Pipeline results
```

## Modules

### models.py

```python
@dataclass
class Record:
    data: dict[str, str]

@dataclass
class Dataset:
    headers: list[str]
    records: list[Record]

@dataclass
class TransformStep:
    name: str
    description: str
    operation: str          # "filter", "aggregate", "sort", "add_column", "rename"
    params: dict

@dataclass
class Pipeline:
    name: str
    description: str
    steps: list[TransformStep]
```

### pipelines.py

5 curated pipeline presets:

| Pipeline | Focus |
|----------|-------|
| Sales Summary | Filter by region, aggregate revenue by product |
| Top Performers | Sort by metric, take top N |
| Data Cleanup | Remove nulls, normalize formats, deduplicate |
| Period Comparison | Filter by date range, compute period-over-period |
| Custom Report | Add computed columns, rename headers, export |

### reader.py

- `read_csv(path)` → Dataset from CSV file
- `read_json(path)` → Dataset from JSON file
- `from_dicts(headers, records)` → Dataset from in-memory data
- `generate_sample_data()` → Realistic sample sales dataset

### transforms.py

- `filter_records(dataset, column, operator, value)` → filtered Dataset
- `sort_records(dataset, column, ascending)` → sorted Dataset
- `aggregate(dataset, group_by, agg_column, operation)` → aggregated Dataset
- `add_column(dataset, name, expression)` → Dataset with computed column
- `rename_columns(dataset, mapping)` → Dataset with renamed headers
- `deduplicate(dataset, columns)` → deduplicated Dataset
- `apply_pipeline(dataset, steps)` → run all steps, return TransformResult

### writer.py

- `write_csv(dataset, path)` → save as CSV
- `write_json(dataset, path)` → save as JSON
- `to_table_string(dataset, max_rows)` → formatted ASCII table

### display.py

- `format_header(title)` → boxed ASCII header
- `format_pipeline_menu(pipelines)` → numbered pipeline list
- `format_stats(dataset)` → record count, column count

## UX Flow

```
$ uv run python run.py

╔══════════════════════════════════════════╗
║        Data Pipeline — Setup            ║
╚══════════════════════════════════════════╝

Choose a pipeline:
  1. Sales Summary       Filter by region, aggregate revenue
  2. Top Performers      Sort by metric, take top N
  3. Data Cleanup        Remove nulls, normalize, deduplicate
  4. Period Comparison   Filter date range, period-over-period
  5. Custom Report       Computed columns, rename, export

Pipeline (1-5): 1

── Sales Summary ──

Loading data...
  Loaded 50 records, 6 columns

Applying transforms:
  ✓ Filter: region = "EMEA"          → 18 records
  ✓ Aggregate: sum revenue by product → 5 records

┌──────────┬─────────┐
│ product  │ revenue │
├──────────┼─────────┤
│ Widget A │ 45,200  │
│ Widget B │ 32,100  │
│ ...      │ ...     │
└──────────┴─────────┘

Results saved to output/2026-03-08_sales-summary.csv
```

## Dependencies

- Zero runtime dependencies (stdlib only)
- Uses `csv`, `json`, `pathlib` from stdlib
- `pytest` (dev)

## Testing Strategy

- CSV/JSON read/write round-trip tests
- Each transform function with edge cases
- Pipeline application with multiple steps
- Sample data generation
- Display formatting
- Target: ~25 tests
