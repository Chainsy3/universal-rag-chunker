"""Source-preserving bounded windows, optionally preferring natural boundaries."""
from __future__ import annotations

import re
from typing import Protocol

from .config import Config
from .models import ChunkDraft, DocumentIR, VERSION


class Strategy(Protocol):
    name: str
    version: str

    def chunk(self, document: DocumentIR, config: Config) -> list[ChunkDraft]: ...


class FixedStrategy:
    name = "fixed"
    version = VERSION

    def chunk(self, document: DocumentIR, config: Config) -> list[ChunkDraft]:
        by_id = {b.block_id: b for b in document.blocks}
        drafts: list[ChunkDraft] = []
        for block in document.blocks:
            path = []
            node = block if block.type == "heading" else by_id.get(block.parent_id)
            while node:
                path.append({"block_id": node.block_id, "title": node.attributes["title"]})
                node = by_id.get(node.parent_id)
            path.reverse()
            start = 0
            while start < len(block.text):
                end = min(start + config.max_characters, len(block.text))
                if self.name == "recursive" and end < len(block.text):
                    floor = start + max(config.overlap_characters + 1, config.minimum_characters, 1)
                    candidates = [m.end() for m in re.finditer(r"\n|[。！？；]+[”’）】]*|[.!?]+[\"\'’”)]*(?=\s|$)", block.text[start:end])
                                  if start + m.end() >= floor]
                    if candidates:
                        end = start + candidates[-1]
                    else:
                        # Prefer English word boundaries when no sentence fits.
                        words = [m.end() for m in re.finditer(r"\s+", block.text[start:end])
                                 if start + m.end() >= floor]
                        if words:
                            end = start + words[-1]
                piece = block.text[start:end]
                if piece.strip():
                    kind = {"code": "code", "table_row": "table"}.get(block.type, "text")
                    drafts.append(ChunkDraft(piece, kind, path,
                                             [{"block_id": block.block_id, "start": start, "end": end, "role": "body"}],
                                             {"core.continuation": start > 0 or end < len(block.text)}))
                if end == len(block.text):
                    break
                start = end - config.overlap_characters
        return drafts


class RecursiveStrategy(FixedStrategy):
    name = "recursive"
    version = VERSION + ".bilingual.1"

    def chunk(self, document: DocumentIR, config: Config) -> list[ChunkDraft]:
        drafts = super().chunk(document, config)
        blocks = {b.block_id: b for b in document.blocks}
        merged: list[ChunkDraft] = []
        for draft in drafts:
            previous = merged[-1] if merged else None
            # Merge only adjacent blocks with exactly the same heading context.
            if (previous and len(previous.text) < config.minimum_characters
                    and previous.kind == draft.kind == "text"
                    and previous.heading_path == draft.heading_path
                    and previous.source_spans[-1]["block_id"] != draft.source_spans[0]["block_id"]
                    and blocks[draft.source_spans[0]["block_id"]].locator["kind"] != "page"
                    and len(previous.text) + len(draft.text) <= config.max_characters):
                previous.text += draft.text
                previous.source_spans.extend(draft.source_spans)
                previous.metadata["core.continuation"] |= draft.metadata["core.continuation"]
            else:
                merged.append(draft)
        return merged
