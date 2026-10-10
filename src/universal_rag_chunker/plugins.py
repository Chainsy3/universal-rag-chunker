"""Plugins are opt-in trusted Python code; mutation is validated afterwards."""
from typing import Protocol

from .config import Config
from .models import ChunkDraft, DocumentIR, VERSION


class Plugin(Protocol):
    name: str
    version: str

    def prepare(self, document: DocumentIR, config: Config) -> DocumentIR: ...
    def enrich(self, document: DocumentIR, drafts: list[ChunkDraft], config: Config) -> list[ChunkDraft]: ...


class ExampleMetadataPlugin:
    name = "example_metadata"
    version = VERSION

    def prepare(self, document: DocumentIR, config: Config) -> DocumentIR:
        return document

    def enrich(self, document: DocumentIR, drafts: list[ChunkDraft], config: Config) -> list[ChunkDraft]:
        for draft in drafts:
            draft.metadata["example.source_name"] = document.source["display_name"]
        return drafts
