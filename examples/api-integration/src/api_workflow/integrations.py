"""Integration presets for the API Integration workflow."""

from api_workflow.models import ApiConfig, Integration, TransformSpec

INTEGRATIONS: list[Integration] = [
    Integration(
        name="GitHub Repos",
        description="Fetch popular repos, extract stars and language",
        api=ApiConfig(
            base_url="https://api.github.com",
            endpoint="/search/repositories",
            params={"q": "stars:>10000", "sort": "stars", "per_page": "10"},
            headers={"Accept": "application/vnd.github.v3+json"},
        ),
        transform=TransformSpec(
            extract_path="items",
            fields=["full_name", "stargazers_count", "language", "description"],
            rename={"stargazers_count": "stars", "full_name": "repo"},
        ),
        sample_response={
            "items": [
                {"full_name": "freeCodeCamp/freeCodeCamp", "stargazers_count": 385000, "language": "TypeScript", "description": "Open-source codebase and curriculum"},
                {"full_name": "996icu/996.ICU", "stargazers_count": 269000, "language": "Rust", "description": "Repo for counting�"},
                {"full_name": "EbookFoundation/free-programming-books", "stargazers_count": 315000, "language": None, "description": "Freely available programming books"},
                {"full_name": "jwasham/coding-interview-university", "stargazers_count": 295000, "language": None, "description": "A complete computer science study plan"},
                {"full_name": "sindresorhus/awesome", "stargazers_count": 290000, "language": None, "description": "Awesome lists about all kinds of topics"},
            ]
        },
    ),
    Integration(
        name="Weather Forecast",
        description="Fetch 7-day forecast for a city",
        api=ApiConfig(
            base_url="https://api.open-meteo.com",
            endpoint="/v1/forecast",
            params={"latitude": "52.52", "longitude": "13.41", "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum", "timezone": "Europe/Berlin"},
        ),
        transform=TransformSpec(
            extract_path="daily",
            fields=["time", "temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            rename={"temperature_2m_max": "max_temp", "temperature_2m_min": "min_temp", "precipitation_sum": "rain_mm"},
        ),
        sample_response={
            "daily": {
                "time": ["2026-03-08", "2026-03-09", "2026-03-10", "2026-03-11", "2026-03-12", "2026-03-13", "2026-03-14"],
                "temperature_2m_max": [8.2, 10.1, 12.5, 9.8, 7.3, 11.0, 13.2],
                "temperature_2m_min": [2.1, 3.5, 5.0, 3.2, 1.8, 4.2, 6.1],
                "precipitation_sum": [0.0, 2.3, 0.5, 5.1, 0.0, 0.0, 1.2],
            }
        },
    ),
    Integration(
        name="Currency Rates",
        description="Fetch exchange rates for major currencies",
        api=ApiConfig(
            base_url="https://open.er-api.com",
            endpoint="/v6/latest/USD",
        ),
        transform=TransformSpec(
            extract_path="rates",
            fields=["EUR", "GBP", "JPY", "CHF", "CAD", "AUD"],
        ),
        sample_response={
            "rates": {
                "EUR": 0.92, "GBP": 0.79, "JPY": 149.50, "CHF": 0.88,
                "CAD": 1.36, "AUD": 1.53, "CNY": 7.24, "INR": 83.12,
            }
        },
    ),
    Integration(
        name="HackerNews Top",
        description="Fetch top stories from Hacker News",
        api=ApiConfig(
            base_url="https://hacker-news.firebaseio.com",
            endpoint="/v0/topstories.json",
        ),
        transform=TransformSpec(
            extract_path="",
            fields=[],
        ),
        sample_response={
            "stories": [
                {"title": "Show HN: A new approach to distributed systems", "score": 342, "by": "pg", "url": "https://example.com/1"},
                {"title": "Why Rust is the future of systems programming", "score": 287, "by": "dang", "url": "https://example.com/2"},
                {"title": "The hidden costs of microservices", "score": 256, "by": "tptacek", "url": "https://example.com/3"},
                {"title": "Building a database from scratch in Go", "score": 198, "by": "jl", "url": "https://example.com/4"},
                {"title": "A deep dive into WebAssembly performance", "score": 175, "by": "cw", "url": "https://example.com/5"},
            ]
        },
    ),
    Integration(
        name="System Status",
        description="Check service health and uptime",
        api=ApiConfig(
            base_url="https://status.example.com",
            endpoint="/api/v1/services",
        ),
        transform=TransformSpec(
            extract_path="services",
            fields=["name", "status", "uptime", "response_time_ms"],
            rename={"response_time_ms": "latency_ms"},
        ),
        sample_response={
            "services": [
                {"name": "API Gateway", "status": "operational", "uptime": "99.98%", "response_time_ms": 45},
                {"name": "Database Primary", "status": "operational", "uptime": "99.99%", "response_time_ms": 12},
                {"name": "Cache Layer", "status": "degraded", "uptime": "99.85%", "response_time_ms": 89},
                {"name": "Auth Service", "status": "operational", "uptime": "99.97%", "response_time_ms": 23},
                {"name": "CDN", "status": "operational", "uptime": "99.99%", "response_time_ms": 8},
                {"name": "Search Index", "status": "maintenance", "uptime": "99.50%", "response_time_ms": 150},
            ]
        },
    ),
]


def get_integration(index: int) -> Integration:
    """Get integration by index, clamping to valid range."""
    clamped = max(0, min(index, len(INTEGRATIONS) - 1))
    return INTEGRATIONS[clamped]
