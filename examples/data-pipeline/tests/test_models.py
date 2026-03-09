"""Tests for pipeline.models."""

from pipeline.models import Dataset, Pipeline, Record, TransformStep


class TestRecord:
    def test_create_record(self):
        rec = Record(data={"name": "Alice", "age": "30"})
        assert rec.data["name"] == "Alice"

    def test_get_value(self):
        rec = Record(data={"revenue": "1000"})
        assert rec.data["revenue"] == "1000"


class TestDataset:
    def test_create_dataset(self):
        ds = Dataset(
            headers=["name", "value"],
            records=[Record(data={"name": "A", "value": "1"})],
        )
        assert ds.headers == ["name", "value"]
        assert len(ds.records) == 1

    def test_column_values(self):
        ds = Dataset(
            headers=["x"],
            records=[
                Record(data={"x": "a"}),
                Record(data={"x": "b"}),
            ],
        )
        assert ds.column_values("x") == ["a", "b"]

    def test_column_values_missing_key(self):
        ds = Dataset(
            headers=["x"],
            records=[Record(data={"x": "a"}), Record(data={})],
        )
        assert ds.column_values("x") == ["a", ""]

    def test_row_count(self):
        ds = Dataset(headers=["a"], records=[Record(data={"a": "1"})] * 5)
        assert ds.row_count == 5

    def test_empty_dataset(self):
        ds = Dataset(headers=["a", "b"], records=[])
        assert ds.row_count == 0
        assert ds.column_values("a") == []


class TestTransformStep:
    def test_create_step(self):
        step = TransformStep(
            name="filter_region",
            description="Filter by region",
            operation="filter",
            params={"column": "region", "operator": "eq", "value": "EMEA"},
        )
        assert step.operation == "filter"
        assert step.params["column"] == "region"


class TestPipeline:
    def test_create_pipeline(self):
        step = TransformStep(name="s", description="d", operation="filter", params={})
        pipe = Pipeline(name="Test", description="A test", steps=[step])
        assert pipe.name == "Test"
        assert len(pipe.steps) == 1
