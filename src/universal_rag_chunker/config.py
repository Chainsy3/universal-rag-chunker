"""Strict TOML configuration; defaults < file < explicit CLI options."""
from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .models import digest


@dataclass(frozen=True)
class Config:
    schema_version: str = "1.0"
    parser: str = "auto"
    strategy: str = "recursive"
    plugins: tuple[str, ...] = ()
    max_characters: int = 1200
    minimum_characters: int = 100
    overlap_characters: int = 100
    format: str = "jsonl"
    include_ir: bool = True

    def __post_init__(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError("Unsupported configuration schema_version")
        if any(type(value) is not int for value in (self.max_characters, self.minimum_characters, self.overlap_characters)):
            raise ValueError("Chunk sizes must be integers")
        if not (self.max_characters > 0 and 0 <= self.minimum_characters <= self.max_characters
                and 0 <= self.overlap_characters < self.max_characters):
            raise ValueError("Require max > 0, 0 <= minimum <= max, 0 <= overlap < max")
        if not isinstance(self.parser, str) or not isinstance(self.strategy, str):
            raise ValueError("Component names must be strings")
        if not isinstance(self.plugins, (tuple, list)) or any(not isinstance(p, str) for p in self.plugins):
            raise ValueError("plugins must be an array of names")
        if len(set(self.plugins)) != len(self.plugins):
            raise ValueError("Duplicate plugin names")
        if self.format not in ("json", "jsonl") or type(self.include_ir) is not bool:
            raise ValueError("Invalid export options")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def semantic_digest(self) -> str:
        return digest({k: v for k, v in self.to_dict().items() if k not in ("format", "include_ir")})

    @classmethod
    def load(cls, path: Path | None = None, **overrides: Any) -> Config:
        values: dict[str, Any] = {}
        if path:
            with path.open("rb") as handle:
                raw = tomllib.load(handle)
            allowed = {"schema_version", "parser", "strategy", "plugins", "chunking", "export"}
            if set(raw) - allowed:
                raise ValueError(f"Unknown configuration keys: {sorted(set(raw) - allowed)}")
            values.update({k: v for k, v in raw.items() if k not in ("chunking", "export")})
            for section, keys in (("chunking", {"max_characters", "minimum_characters", "overlap_characters"}),
                                  ("export", {"format", "include_ir"})):
                table = raw.get(section, {})
                if not isinstance(table, dict) or set(table) - keys:
                    raise ValueError(f"Invalid [{section}] options")
                values.update(table)
        values.update({k: v for k, v in overrides.items() if v is not None})
        if isinstance(values.get("plugins"), list):
            values["plugins"] = tuple(values["plugins"])
        return cls(**values)
