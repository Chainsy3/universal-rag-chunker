# Differences between the 0.2.0 implementation and design

[中文](implementation.cn.md) · [English](implementation.en.md)

This is an independent implementation. It does not modify `domain_chunking` or copy its railway-specific business samples. The original design is retained in the parent workspace's `design` directory as a historical proposal; that directory is not part of this public repository.

Text parsing preserves the complete source. Version 0.2.0 adds PDF pages, DOCX body/table rows and XLSX worksheet/row/column locations using Schema 1.1. Binary IR stores actual extracted content, without claiming to preserve all visible content in the original file.

Markdown parsing uses limited rules for ATX headings, fenced code and simple lists; it is not a full CommonMark implementation. `recursive` uses structural blocks, newlines, Chinese/English sentence boundaries and word whitespace, rather than a semantic model. Short blocks may merge, but whitespace-only blocks are not separately exported, so some whitespace between blocks may be absent from final text. Source spans still exactly reconstruct each output chunk.

Validator is a fixed built-in stage. Parser, Strategy and Plugin support registration. Exporter currently offers one `export` API selecting JSON/JSONL; there are no third-party Validator/Exporter registries yet. CI does not run static type checking; it runs compilation checks, tests, package builds and CLI tests against the installed package.

Possible future work: broader Markdown support, configurable sentence boundaries, independent Validator/Exporter Protocols, question-bank plugins, OCR, PDF table structure, explicit header configuration and legacy DOC/XLS conversion. Unimplemented capabilities are not current commitments.
