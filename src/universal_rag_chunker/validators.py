"""Validate the shipped JSON Schema subset plus semantic source invariants."""
from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path

from .models import DocumentIR, Chunk, canonical, digest


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def check_schema(value, schema, path="$", root=None):
    """Small evaluator for the keywords used in our bundled schemas only."""
    root = schema if root is None else root
    if "oneOf" in schema:
        matches = 0
        for option in schema["oneOf"]:
            try:
                check_schema(value, option, path, root)
                matches += 1
            except ValidationError:
                pass
        require(matches == 1, f"{path}: expected exactly one locator variant")
        return
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        return check_schema(value, target, path, root)
    types = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
             "string": lambda v: isinstance(v, str), "integer": lambda v: type(v) is int,
             "boolean": lambda v: type(v) is bool, "null": lambda v: v is None}
    expected = schema.get("type")
    if expected:
        options = expected if isinstance(expected, list) else [expected]
        require(any(types[t](value) for t in options), f"{path}: expected {expected}")
    if "const" in schema:
        require(value == schema["const"], f"{path}: unsupported value")
    if "enum" in schema:
        require(value in schema["enum"], f"{path}: unsupported value")
    if isinstance(value, dict):
        require(set(schema.get("required", [])) <= set(value), f"{path}: missing required keys")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            require(set(value) <= set(properties), f"{path}: unknown keys")
        for key, item in value.items():
            if key in properties:
                check_schema(item, properties[key], path + "." + key, root)
    if isinstance(value, list):
        require(len(value) >= schema.get("minItems", 0), f"{path}: too few items")
        for i, item in enumerate(value):
            check_schema(item, schema.get("items", {}), f"{path}[{i}]", root)
    if isinstance(value, str):
        require(len(value) >= schema.get("minLength", 0), f"{path}: empty string")
        if "pattern" in schema:
            require(re.search(schema["pattern"], value) is not None, f"{path}: invalid format")
    if type(value) is int:
        require(value >= schema.get("minimum", value), f"{path}: below minimum")


def schema_validate(value, name):
    version = value.get("schema_version")
    require(version in ("1.0", "1.1"), "Unsupported schema_version")
    schema = json.loads((Path(__file__).parent / "schemas" / f"{name}-{version}.schema.json").read_text(encoding="utf-8"))
    check_schema(value, schema)
    try:
        canonical(value)
    except (TypeError, ValueError) as error:
        raise ValidationError("Metadata must contain finite JSON values") from error


def validate_ir(document: DocumentIR):
    require(bool(document.blocks), "EMPTY_DOCUMENT")
    schema_validate(document.to_dict(), "document-ir")
    seen = {}
    previous_end = 0
    kinds = {b.locator["kind"] for b in document.blocks}
    require(len(kinds) == 1, "Mixed source locator types are unsupported")
    locator_kind = next(iter(kinds))
    previous_position = None
    sheet_rows = {}
    last_sheet = None
    for index, block in enumerate(document.blocks):
        require(block.order == index, "IR order must be continuous")
        require(block.block_id not in seen, "Duplicate block_id")
        require(block.parent_id is None or block.parent_id in seen, "Parent must precede child (no cycles)")
        if block.parent_id:
            require(seen[block.parent_id].type == "heading", "Parent must be a heading")
        locator = block.locator
        if locator_kind == "text":
            require(locator["start"] == previous_end and locator["end"] - locator["start"] == len(block.text),
                    "Text IR must partition original source without rewriting")
            previous_end = locator["end"]
        elif locator_kind == "page":
            require(locator["page"] == index + 1, "PDF pages must be continuous, including empty pages")
        elif locator_kind == "docx":
            position = (locator["body_index"], locator.get("row", 0))
            require(previous_position is None or position > previous_position, "DOCX body order is invalid")
            previous_position = position
            require((block.type == "table_row") == ("row" in locator), "DOCX row locator/type mismatch")
        elif locator_kind == "sheet":
            require(locator["column_start"] <= locator["column_end"], "Invalid sheet column range")
            require(block.type == "table_row", "Sheet block must be a table row")
            name = locator["sheet_name"]
            require(name not in sheet_rows or name == last_sheet, "Sheet rows must stay together")
            require(locator["row"] > sheet_rows.get(name, 0), "Sheet row order is invalid")
            sheet_rows[name] = locator["row"]
            last_sheet = name
        if block.type == "heading":
            require(type(block.attributes.get("level")) is int and 1 <= block.attributes["level"] <= 6
                    and isinstance(block.attributes.get("title"), str), "Invalid heading attributes")
        seen[block.block_id] = block
    require(any(b.text.strip() for b in document.blocks), "EMPTY_DOCUMENT")
    raw_hash = hashlib.sha256("".join(b.text for b in document.blocks).encode("utf-8")).hexdigest()
    if locator_kind == "text":
        require(raw_hash == document.source["content_sha256"], "IR source hash mismatch")
    else:
        require(raw_hash == document.source.get("extracted_text_sha256"), "Extracted text hash mismatch")
    expected_id = "doc_" + digest([document.source["source_id"], document.source["content_sha256"], document.parser])
    require(document.document_id == expected_id, "Document ID mismatch")
    for block in document.blocks:
        expected_id = "block_" + digest([document.document_id, block.order, block.type, block.text,
                                         block.locator, block.parent_id, block.attributes])
        require(block.block_id == expected_id, "Block ID mismatch")


def validate_chunks(document: DocumentIR, chunks: list[Chunk], max_characters: int):
    validate_ir(document)
    blocks = {b.block_id: b for b in document.blocks}
    coverage = {key: set() for key in blocks}
    ids = set()
    last_source = (-1, -1)
    for index, chunk in enumerate(chunks):
        schema_validate(chunk.to_dict(), "chunk")
        require(chunk.schema_version == document.schema_version, "Chunk/IR schema versions differ")
        require(chunk.order == index and chunk.document_id == document.document_id, "Invalid chunk order/document")
        require(chunk.chunk_id not in ids, "Duplicate chunk_id")
        ids.add(chunk.chunk_id)
        require(chunk.chunk_id == "chunk_" + digest([document.document_id, chunk.text, chunk.source_spans,
                                                     chunk.provenance, index]), "Chunk ID mismatch")
        require(bool(chunk.text.strip()), "Empty chunk")
        require(len(chunk.text) <= max_characters, "Chunk exceeds character limit")
        require(chunk.size["characters"] == len(chunk.text), "Incorrect character count")
        pieces = []
        positions = []
        for span in chunk.source_spans:
            require(span["block_id"] in blocks, "Unknown source block")
            block = blocks[span["block_id"]]
            start, end = span["start"], span["end"]
            require(0 <= start < end <= len(block.text), "Invalid source range")
            positions.append((block.order, start))
            pieces.append(block.text[start:end])
            coverage[block.block_id].update(range(start, end))
        require(positions == sorted(positions), "Source spans out of order")
        require(positions[0] >= last_source, "Chunks out of source order")
        last_source = positions[0]
        require("".join(pieces) == chunk.text, "Chunk text cannot be reconstructed from source")
        expected_path = []
        first = blocks[chunk.source_spans[0]["block_id"]]
        node = first if first.type == "heading" else blocks.get(first.parent_id)
        while node:
            expected_path.append({"block_id": node.block_id, "title": node.attributes["title"]})
            node = blocks.get(node.parent_id)
        require(chunk.heading_path == list(reversed(expected_path)), "Incorrect heading path")
    expected = sum(not c.isspace() for b in document.blocks for c in b.text)
    covered = sum(not c.isspace() and i in coverage[b.block_id] for b in document.blocks for i, c in enumerate(b.text))
    require(covered == expected, "Unexplained loss of non-whitespace source content")
    sizes = [len(c.text) for c in chunks]
    return {"valid": True, "chunk_count": len(chunks), "min_characters": min(sizes, default=0),
            "max_characters": max(sizes, default=0), "coverage": covered / expected if expected else 1.0,
            "coverage_unit": "non_whitespace_codepoints",
            "coverage_scope": "original_text" if document.blocks[0].locator["kind"] == "text" else "parser_extracted_text",
            "diagnostics": document.metadata.get("diagnostics", [])}
