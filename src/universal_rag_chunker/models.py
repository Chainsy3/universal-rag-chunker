"""Versioned, JSON-compatible data contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

VERSION = "0.2.0"
SCHEMA_VERSION = "1.1"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


@dataclass
class Block:
    block_id: str
    type: str
    order: int
    parent_id: str | None
    text: str
    locator: dict[str, Any]
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentIR:
    document_id: str
    source: dict[str, Any]
    parser: dict[str, Any]
    blocks: list[Block]
    metadata: dict[str, Any] = field(default_factory=dict)
    document_type: str = "unknown"
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> DocumentIR:
        data = dict(value)
        data["blocks"] = [Block(**item) for item in data["blocks"]]
        return cls(**data)


@dataclass
class ChunkDraft:
    text: str
    kind: str
    heading_path: list[dict[str, str]]
    source_spans: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    order: int
    text: str
    kind: str
    heading_path: list[dict[str, str]]
    source_spans: list[dict[str, Any]]
    size: dict[str, int]
    provenance: dict[str, Any]
    metadata: dict[str, Any]
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    document: DocumentIR
    chunks: list[Chunk]
    report: dict[str, Any]
    config: dict[str, Any]
