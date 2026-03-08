# API Integration Example — Design

**Date:** 2026-03-08
**Pattern:** `trigger → api → transform → data`
**Status:** Approved

## Goal

Sixth runnable example for workflow-patterns. A REST API data collector that fetches from APIs, transforms JSON responses, and stores structured results. Works offline with sample data fallback. Demonstrates `api → transform → data` — fetch, reshape, persist.

## Architecture

```
select_integration() → fetch_api() → transform_response() → save_results()
trigger                api            transform               data
```

## Module Structure

```
examples/api-integration/
├── run.py                      # CLI entry point
├── .env.example                # Optional API tokens
├── .gitignore                  # .env, __pycache__, output/
├── pyproject.toml              # Zero runtime dependencies (stdlib only)
├── src/api_workflow/
│   ├── __init__.py
│   ├── models.py               # ApiConfig, ApiResponse, Integration
│   ├── integrations.py         # 5 integration presets
│   ├── client.py               # HTTP client with sample fallback (API layer)
│   ├── transform.py            # JSON response transformers
│   ├── storage.py              # Save results to file (data layer)
│   └── display.py              # Terminal formatting
├── tests/
│   ├── test_models.py
│   ├── test_integrations.py
│   ├── test_client.py
│   ├── test_transform.py
│   ├── test_storage.py
│   ├── test_display.py
│   └── __init__.py
└── output/                     # Saved API results
```

## Dependencies

- Zero runtime dependencies (uses urllib.request from stdlib)
- `pytest` (dev)
