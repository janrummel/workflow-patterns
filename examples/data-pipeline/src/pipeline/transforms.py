"""Data transformations for the Data Pipeline workflow (transform layer).

Pure functions that take a Dataset and return a new Dataset.
"""

from dataclasses import dataclass

from pipeline.models import Dataset, Record, TransformStep


@dataclass
class StepResult:
    step_name: str
    input_count: int
    output_count: int


@dataclass
class TransformResult:
    dataset: Dataset
    step_results: list[StepResult]


def filter_records(
    dataset: Dataset, column: str, operator: str, value: str
) -> Dataset:
    """Filter records by column value."""
    filtered = []
    for rec in dataset.records:
        cell = rec.data.get(column, "")
        match operator:
            case "eq":
                if cell == value:
                    filtered.append(rec)
            case "neq":
                if cell != value:
                    filtered.append(rec)
            case "gt":
                try:
                    if float(cell) > float(value):
                        filtered.append(rec)
                except ValueError:
                    pass
            case "lt":
                try:
                    if float(cell) < float(value):
                        filtered.append(rec)
                except ValueError:
                    pass
            case "contains":
                if value in cell:
                    filtered.append(rec)
    return Dataset(headers=dataset.headers, records=filtered)


def sort_records(
    dataset: Dataset, column: str, ascending: bool = True, numeric: bool = False
) -> Dataset:
    """Sort records by column value."""
    def key_fn(rec: Record):
        val = rec.data.get(column, "")
        if numeric:
            try:
                return float(val)
            except ValueError:
                return 0.0
        return val

    sorted_recs = sorted(dataset.records, key=key_fn, reverse=not ascending)
    return Dataset(headers=dataset.headers, records=sorted_recs)


def aggregate(
    dataset: Dataset, group_by: str, agg_column: str, operation: str
) -> Dataset:
    """Aggregate records by grouping column."""
    groups: dict[str, list[str]] = {}
    for rec in dataset.records:
        key = rec.data.get(group_by, "")
        groups.setdefault(key, []).append(rec.data.get(agg_column, "0"))

    records = []
    for group_key, values in groups.items():
        match operation:
            case "sum":
                result = str(int(sum(float(v) for v in values)))
            case "count":
                result = str(len(values))
            case "avg":
                result = str(sum(float(v) for v in values) / len(values))
            case _:
                result = str(len(values))
        records.append(Record(data={group_by: group_key, agg_column: result}))

    return Dataset(headers=[group_by, agg_column], records=records)


def add_column(
    dataset: Dataset,
    name: str,
    expr_cols: list[str],
    expr_op: str,
    separator: str = "",
) -> Dataset:
    """Add a computed column to the dataset."""
    new_records = []
    for rec in dataset.records:
        new_data = dict(rec.data)
        vals = [rec.data.get(c, "") for c in expr_cols]
        match expr_op:
            case "multiply":
                try:
                    result = 1
                    for v in vals:
                        result *= int(float(v))
                    new_data[name] = str(result)
                except ValueError:
                    new_data[name] = "0"
            case "concat":
                new_data[name] = separator.join(vals)
            case _:
                new_data[name] = separator.join(vals)
        new_records.append(Record(data=new_data))

    headers = dataset.headers + [name]
    return Dataset(headers=headers, records=new_records)


def rename_columns(dataset: Dataset, mapping: dict[str, str]) -> Dataset:
    """Rename columns in the dataset."""
    new_headers = [mapping.get(h, h) for h in dataset.headers]
    new_records = []
    for rec in dataset.records:
        new_data = {}
        for key, value in rec.data.items():
            new_key = mapping.get(key, key)
            new_data[new_key] = value
        new_records.append(Record(data=new_data))
    return Dataset(headers=new_headers, records=new_records)


def deduplicate(dataset: Dataset, columns: list[str]) -> Dataset:
    """Remove duplicate records based on specified columns."""
    seen: set[tuple[str, ...]] = set()
    unique = []
    for rec in dataset.records:
        key = tuple(rec.data.get(c, "") for c in columns)
        if key not in seen:
            seen.add(key)
            unique.append(rec)
    return Dataset(headers=dataset.headers, records=unique)


def apply_pipeline(dataset: Dataset, steps: list[TransformStep]) -> TransformResult:
    """Apply a sequence of transform steps to a dataset."""
    current = dataset
    step_results = []

    for step in steps:
        input_count = current.row_count
        match step.operation:
            case "filter":
                current = filter_records(
                    current,
                    step.params["column"],
                    step.params["operator"],
                    step.params["value"],
                )
            case "sort":
                current = sort_records(
                    current,
                    step.params["column"],
                    step.params.get("ascending", True),
                    step.params.get("numeric", False),
                )
            case "aggregate":
                current = aggregate(
                    current,
                    step.params["group_by"],
                    step.params["agg_column"],
                    step.params["operation"],
                )
            case "add_column":
                current = add_column(
                    current,
                    step.params["name"],
                    step.params["expr_cols"],
                    step.params["expr_op"],
                    step.params.get("separator", ""),
                )
            case "rename":
                current = rename_columns(current, step.params["mapping"])
            case "deduplicate":
                current = deduplicate(current, step.params["columns"])

        step_results.append(
            StepResult(
                step_name=step.name,
                input_count=input_count,
                output_count=current.row_count,
            )
        )

    return TransformResult(dataset=current, step_results=step_results)
