"""HTTP client for the API Integration workflow (API layer).

Fetches from REST APIs with fallback to sample data.
Uses urllib.request from stdlib — no external dependencies.
"""

import json
import urllib.request
import urllib.error

from api_workflow.models import ApiConfig, ApiResponse


def fetch_sample(sample_data: dict | list) -> ApiResponse:
    """Return sample data as an ApiResponse."""
    return ApiResponse(status=200, data=sample_data, source="sample")


def fetch(cfg: ApiConfig, sample_data: dict | list | None = None) -> ApiResponse:
    """Fetch from API, falling back to sample data on failure."""
    try:
        req = urllib.request.Request(cfg.full_url, headers=cfg.headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return ApiResponse(status=resp.status, data=data, source="live")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        if sample_data is not None:
            return fetch_sample(sample_data)
        return ApiResponse(status=0, data={"error": "Request failed"}, source="error")
