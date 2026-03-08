"""Tests for pipeline.transforms."""

from pipeline.models import Dataset, Record, TransformStep
from pipeline.transforms import (
    add_column,
    aggregate,
    apply_pipeline,
    deduplicate,
    filter_records,
    rename_columns,
    sort_records,
)


def _ds(rows: list[dict[str, str]], headers: list[str] | None = None) -> Dataset:
    if headers is None:
        headers = list(rows[0].keys()) if rows else []
    return Dataset(headers=headers, records=[Record(data=r) for r in rows])


class TestFilterRecords:
    def test_filter_eq(self):
        ds = _ds([{"region": "EMEA"}, {"region": "NA"}, {"region": "EMEA"}])
        result = filter_records(ds, "region", "eq", "EMEA")
        assert result.row_count == 2

    def test_filter_neq(self):
        ds = _ds([{"region": "EMEA"}, {"region": "NA"}])
        result = filter_records(ds, "region", "neq", "EMEA")
        assert result.row_count == 1

    def test_filter_gt(self):
        ds = _ds([{"value": "100"}, {"value": "200"}, {"value": "50"}])
        result = filter_records(ds, "value", "gt", "99")
        assert result.row_count == 2

    def test_filter_lt(self):
        ds = _ds([{"value": "100"}, {"value": "200"}, {"value": "50"}])
        result = filter_records(ds, "value", "lt", "100")
        assert result.row_count == 1

    def test_filter_contains(self):
        ds = _ds([{"name": "Widget A"}, {"name": "Service X"}])
        result = filter_records(ds, "name", "contains", "Widget")
        assert result.row_count == 1

    def test_filter_empty_result(self):
        ds = _ds([{"x": "a"}])
        result = filter_records(ds, "x", "eq", "b")
        assert result.row_count == 0


class TestSortRecords:
    def test_sort_ascending(self):
        ds = _ds([{"v": "30"}, {"v": "10"}, {"v": "20"}])
        result = sort_records(ds, "v", ascending=True)
        assert [r.data["v"] for r in result.records] == ["10", "20", "30"]

    def test_sort_descending(self):
        ds = _ds([{"v": "30"}, {"v": "10"}, {"v": "20"}])
        result = sort_records(ds, "v", ascending=False)
        assert [r.data["v"] for r in result.records] == ["30", "20", "10"]

    def test_sort_numeric(self):
        ds = _ds([{"v": "100"}, {"v": "20"}, {"v": "3"}])
        result = sort_records(ds, "v", ascending=True, numeric=True)
        assert [r.data["v"] for r in result.records] == ["3", "20", "100"]


class TestAggregate:
    def test_sum(self):
        ds = _ds([
            {"group": "A", "val": "10"},
            {"group": "A", "val": "20"},
            {"group": "B", "val": "5"},
        ])
        result = aggregate(ds, group_by="group", agg_column="val", operation="sum")
        assert result.row_count == 2
        a_row = next(r for r in result.records if r.data["group"] == "A")
        assert a_row.data["val"] == "30"

    def test_count(self):
        ds = _ds([
            {"group": "A", "val": "10"},
            {"group": "A", "val": "20"},
            {"group": "B", "val": "5"},
        ])
        result = aggregate(ds, group_by="group", agg_column="val", operation="count")
        a_row = next(r for r in result.records if r.data["group"] == "A")
        assert a_row.data["val"] == "2"

    def test_avg(self):
        ds = _ds([
            {"group": "A", "val": "10"},
            {"group": "A", "val": "30"},
        ])
        result = aggregate(ds, group_by="group", agg_column="val", operation="avg")
        assert result.records[0].data["val"] == "20.0"


class TestAddColumn:
    def test_add_computed_column(self):
        ds = _ds([{"units": "10", "price": "5"}], headers=["units", "price"])
        result = add_column(ds, "total", expr_cols=["units", "price"], expr_op="multiply")
        assert "total" in result.headers
        assert result.records[0].data["total"] == "50"

    def test_add_concat_column(self):
        ds = _ds([{"a": "hello", "b": "world"}], headers=["a", "b"])
        result = add_column(ds, "combined", expr_cols=["a", "b"], expr_op="concat", separator=" ")
        assert result.records[0].data["combined"] == "hello world"


class TestRenameColumns:
    def test_rename(self):
        ds = _ds([{"old_name": "val"}], headers=["old_name"])
        result = rename_columns(ds, {"old_name": "new_name"})
        assert "new_name" in result.headers
        assert "old_name" not in result.headers
        assert result.records[0].data["new_name"] == "val"


class TestDeduplicate:
    def test_removes_duplicates(self):
        ds = _ds([
            {"id": "1", "name": "A"},
            {"id": "1", "name": "A"},
            {"id": "2", "name": "B"},
        ])
        result = deduplicate(ds, columns=["id"])
        assert result.row_count == 2

    def test_no_duplicates(self):
        ds = _ds([{"id": "1"}, {"id": "2"}])
        result = deduplicate(ds, columns=["id"])
        assert result.row_count == 2


class TestApplyPipeline:
    def test_multi_step_pipeline(self):
        ds = _ds([
            {"region": "EMEA", "revenue": "100"},
            {"region": "NA", "revenue": "200"},
            {"region": "EMEA", "revenue": "150"},
        ])
        steps = [
            TransformStep(
                name="filter", description="EMEA only",
                operation="filter",
                params={"column": "region", "operator": "eq", "value": "EMEA"},
            ),
            TransformStep(
                name="sort", description="By revenue",
                operation="sort",
                params={"column": "revenue", "ascending": False, "numeric": True},
            ),
        ]
        result = apply_pipeline(ds, steps)
        assert result.dataset.row_count == 2
        assert result.dataset.records[0].data["revenue"] == "150"
        assert len(result.step_results) == 2
