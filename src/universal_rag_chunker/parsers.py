"""Conservative lossless UTF-8 parsers. Block text retains source markup."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Protocol

from .models import Block, DocumentIR, VERSION, digest


class Parser(Protocol):
    name: str
    version: str
    suffixes: tuple[str, ...]

    def parse(self, source: Path, source_id: str) -> DocumentIR: ...


class TextParser:
    name = "text"
    version = VERSION
    suffixes = (".txt",)
    media_type = "text/plain"

    def parse(self, source: Path, source_id: str) -> DocumentIR:
        raw = source.read_bytes()
        text = raw.decode("utf-8")  # No newline normalization; offsets remain exact.
        parser = {"name": self.name, "version": self.version, "config_digest": digest({})}
        metadata = {"source_id": source_id, "display_name": source.name,
                    "media_type": self.media_type, "content_sha256": hashlib.sha256(raw).hexdigest()}
        document_id = "doc_" + digest([source_id, metadata["content_sha256"], parser])
        blocks = self._blocks(text, document_id)
        return DocumentIR(document_id, metadata, parser, blocks)

    def _blocks(self, text: str, document_id: str) -> list[Block]:
        return make_blocks(text, document_id, markdown=False)


class MarkdownParser(TextParser):
    name = "markdown"
    suffixes = (".md", ".markdown")
    media_type = "text/markdown"

    def _blocks(self, text: str, document_id: str) -> list[Block]:
        return make_blocks(text, document_id, markdown=True)


def make_blocks(text: str, document_id: str, *, markdown: bool) -> list[Block]:
    blocks: list[Block] = []
    hierarchy: list[tuple[int, str]] = []
    cursor = 0
    lines = text.splitlines(keepends=True)
    index = 0
    while index < len(lines):
        line = lines[index]
        attributes = {}
        kind = "paragraph"
        consumed = 1
        heading = re.match(r" {0,3}(#{1,6})[ \t]+(.+?)[ \t]*\r?\n?$", line) if markdown else None
        fence = re.match(r" {0,3}(`{3,}|~{3,})([^\r\n]*)", line) if markdown else None
        if fence:
            kind = "code"
            marker = fence[1]
            attributes["language"] = fence[2].strip()
            while index + consumed < len(lines):
                candidate = lines[index + consumed]
                consumed += 1
                if re.fullmatch(r" {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*\r?\n?", candidate):
                    break
        elif heading:
            kind = "heading"
            level = len(heading[1])
            attributes = {"level": level, "title": re.sub(r"[ \t]+#+[ \t]*$", "", heading[2])}
            while hierarchy and hierarchy[-1][0] >= level:
                hierarchy.pop()
        elif markdown and re.match(r"\s*(?:[-+*]|\d+[.)])[ \t]+", line):
            kind = "list_item"
        else:
            # Group ordinary lines; preserve blank lines and all original characters.
            while index + consumed < len(lines):
                candidate = lines[index + consumed]
                if not candidate.strip() or not lines[index + consumed - 1].strip():
                    break
                if markdown and re.match(r" {0,3}(?:#{1,6}[ \t]|`{3,}|~{3,}|[-+*][ \t]|\d+[.)][ \t])", candidate):
                    break
                consumed += 1
        body = "".join(lines[index:index + consumed])
        locator = {"kind": "text", "start": cursor, "end": cursor + len(body)}
        parent = hierarchy[-1][1] if hierarchy else None
        block_id = "block_" + digest([document_id, len(blocks), kind, body, locator, parent, attributes])
        blocks.append(Block(block_id, kind, len(blocks), parent, body, locator, attributes))
        if heading and not fence:
            hierarchy.append((attributes["level"], block_id))
        cursor += len(body)
        index += consumed
    return blocks
