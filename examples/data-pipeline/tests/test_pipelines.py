"""Tests for pipeline.pipelines."""

from pipeline.models import Pipeline
from pipeline.pipelines import PIPELINES, get_pipeline


class TestPipelines:
    def test_five_pipelines(self):
        assert len(PIPELINES) == 5

    def test_all_are_pipeline_instances(self):
        for p in PIPELINES:
            assert isinstance(p, Pipeline)

    def test_all_have_steps(self):
        for p in PIPELINES:
            assert len(p.steps) >= 1, f"{p.name} has no steps"

    def test_names_unique(self):
        names = [p.name for p in PIPELINES]
        assert len(names) == len(set(names))

    def test_get_pipeline_by_index(self):
        assert get_pipeline(0) == PIPELINES[0]

    def test_get_pipeline_clamps(self):
        assert get_pipeline(-1) == PIPELINES[0]
        assert get_pipeline(99) == PIPELINES[-1]
