"""Tests for api_workflow.client."""

from api_workflow.client import fetch, fetch_sample
from api_workflow.models import ApiConfig, ApiResponse


class TestFetchSample:
    def test_returns_sample_data(self):
        sample = {"items": [{"id": 1}]}
        resp = fetch_sample(sample)
        assert resp.status == 200
        assert resp.data == sample
        assert resp.source == "sample"


class TestFetch:
    def test_falls_back_to_sample(self):
        cfg = ApiConfig(base_url="https://invalid.example.com", endpoint="/nope")
        sample = {"fallback": True}
        resp = fetch(cfg, sample_data=sample)
        assert resp.source == "sample"
        assert resp.data == sample

    def test_no_sample_returns_error(self):
        cfg = ApiConfig(base_url="https://invalid.example.com", endpoint="/nope")
        resp = fetch(cfg)
        assert resp.is_success is False
