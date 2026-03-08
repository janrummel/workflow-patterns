"""Tests for api_workflow.models."""

from api_workflow.models import ApiConfig, ApiResponse, Integration, TransformSpec


class TestApiConfig:
    def test_create(self):
        cfg = ApiConfig(base_url="https://api.example.com", endpoint="/data", headers={})
        assert cfg.base_url == "https://api.example.com"
        assert cfg.endpoint == "/data"

    def test_full_url(self):
        cfg = ApiConfig(base_url="https://api.example.com", endpoint="/v1/items")
        assert cfg.full_url == "https://api.example.com/v1/items"

    def test_full_url_with_params(self):
        cfg = ApiConfig(
            base_url="https://api.example.com",
            endpoint="/search",
            params={"q": "test", "limit": "10"},
        )
        url = cfg.full_url
        assert "q=test" in url
        assert "limit=10" in url


class TestApiResponse:
    def test_create(self):
        resp = ApiResponse(status=200, data={"key": "value"}, source="live")
        assert resp.status == 200
        assert resp.data["key"] == "value"
        assert resp.source == "live"

    def test_is_success(self):
        assert ApiResponse(status=200, data={}).is_success is True
        assert ApiResponse(status=404, data={}).is_success is False


class TestTransformSpec:
    def test_create(self):
        spec = TransformSpec(extract_path="data.items", fields=["name", "value"])
        assert spec.extract_path == "data.items"
        assert spec.fields == ["name", "value"]


class TestIntegration:
    def test_create(self):
        cfg = ApiConfig(base_url="https://example.com", endpoint="/")
        spec = TransformSpec(extract_path="data", fields=["id"])
        integ = Integration(name="Test", description="A test", api=cfg, transform=spec)
        assert integ.name == "Test"
