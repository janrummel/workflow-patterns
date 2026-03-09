"""Domain models for the API Integration workflow."""

from dataclasses import dataclass, field
from urllib.parse import urlencode


@dataclass
class ApiConfig:
    base_url: str
    endpoint: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)

    @property
    def full_url(self) -> str:
        url = f"{self.base_url}{self.endpoint}"
        if self.params:
            url += "?" + urlencode(self.params)
        return url


@dataclass
class ApiResponse:
    status: int
    data: dict | list
    source: str = "live"  # "live" or "sample"

    @property
    def is_success(self) -> bool:
        return 200 <= self.status < 300


@dataclass
class TransformSpec:
    extract_path: str
    fields: list[str]
    rename: dict[str, str] = field(default_factory=dict)


@dataclass
class Integration:
    name: str
    description: str
    api: ApiConfig
    transform: TransformSpec
    sample_response: dict | list | None = None
