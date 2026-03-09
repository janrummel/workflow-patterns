"""Response transformers for the API Integration workflow (transform layer).

Pure functions to extract, filter, and reshape API response data.
"""

from api_workflow.models import TransformSpec


def extract_path(data: dict | list, path: str) -> list:
    """Navigate a dot-separated path and return the result as a list."""
    if not path:
        return data if isinstance(data, list) else [data]

    current = data
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return []

    if isinstance(current, list):
        return current
    return [current]


def pick_fields(records: list[dict], fields: list[str]) -> list[dict]:
    """Pick specified fields from each record. Empty fields list returns all."""
    if not fields:
        return records
    return [{f: rec.get(f, "") for f in fields} for rec in records]


def transform_response(data: dict | list, spec: TransformSpec) -> list[dict]:
    """Full transform: extract path, pick fields, rename."""
    records = extract_path(data, spec.extract_path)
    records = pick_fields(records, spec.fields)

    if spec.rename:
        renamed = []
        for rec in records:
            new_rec = {}
            for k, v in rec.items():
                new_key = spec.rename.get(k, k)
                new_rec[new_key] = v
            renamed.append(new_rec)
        records = renamed

    return records
