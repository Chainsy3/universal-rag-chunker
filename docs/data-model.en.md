# Data contracts 1.1 (compatible reading of 1.0)

[中文](data-model.cn.md) · [English](data-model.en.md)

DocumentIR stores `source`, `parser`, `blocks`, `metadata` and `document_type`. Each block has a unique ID, contiguous `order`, `parent_id`, `type`, `text`, `locator` and `attributes`. A parent must be a heading that appeared earlier, preventing cycles. Heading attributes include `level` and `title`.

Original UTF-8 files use zero-based, half-open Unicode code point offsets. Each text locator identifies an original string slice; line endings are not normalized. Concatenating all `block.text` values must reconstruct the original source text, whose hash must match `source.content_sha256`. A UTF-8 BOM is preserved as a source character.

Binary formats add locators: `page` uses a one-based page number; `docx` uses a one-based `body_index` shared by body paragraphs and tables, plus a one-based `row` for table rows; `sheet` uses `sheet_name`, one-based `row`, and `column_start`/`column_end`. Table blocks have `type=table_row`; their chunks have `kind=table`. Labels such as DOCX `RnCm` and Excel `A1` belong to the deterministic extraction representation, not contiguous character offsets in the original file. Nested DOCX table text belongs to its top-level cell and has no independent nested row/column locator.

For binary input, `source.content_sha256` hashes the original bytes; the additional `source.extracted_text_sha256` verifies concatenated block text. Offline validation can verify extracted-text integrity and source structure, but cannot prove extraction covers every part of the original file without that file. Empty PDF pages retain empty blocks to preserve page numbering; entirely textless documents are rejected.

Chunk stores `text`, `kind`, `heading_path`, `source_spans`, `size`, `provenance` and `metadata`. Span `start`/`end` offsets refer to IR `block.text`; V1 only permits the `body` role. Concatenating referenced slices in order must exactly reconstruct `chunk.text`. Block locators and local span offsets are different coordinate systems.

Metadata must contain finite, JSON-serializable values. Namespace domain keys, for example `exam.question_number`; the example plugin uses `example.source_name`.

SHA-256 rules are implemented in `models.digest` and `pipeline.py`: canonical JSON uses sorted keys, compact separators, UTF-8 and unescaped non-ASCII characters. Document IDs depend on `source_id`, source-file hash and parser description. Block IDs include order, text, location and structural attributes. Chunk IDs include final text, source references, component provenance and order. Chunk metadata is excluded from the identity hash, so changing display metadata does not change body identity.

Configuration digests exclude `format` and `include_ir`. Paths, timestamps and `run_id` are excluded from semantic configuration. The validate command verifies IDs and source content, not only field shapes.

Coverage is the proportion of all non-whitespace IR characters referenced by at least one span. Repeated overlap counts only once; whitespace may be omitted. `report.coverage_scope` is `original_text` for text input and `parser_extracted_text` for binary input. Parsing diagnostics are retained in `report.diagnostics`. Coverage is neither original-file recognition completeness nor semantic-quality evaluation.
