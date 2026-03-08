"""Domain models for the Data Pipeline workflow."""

from dataclasses import dataclass, field


@dataclass
class Record:
    data: dict[str, str]


@dataclass
class Dataset:
    headers: list[str]
    records: list[Record]

    def column_values(self, column: str) -> list[str]:
        """Get all values for a column."""
        return [r.data.get(column, "") for r in self.records]

    @property
    def row_count(self) -> int:
        return len(self.records)


@dataclass
class TransformStep:
    name: str
    description: str
    operation: str  # "filter", "aggregate", "sort", "add_column", "rename", "deduplicate"
    params: dict = field(default_factory=dict)


@dataclass
class Pipeline:
    name: str
    description: str
    steps: list[TransformStep]
