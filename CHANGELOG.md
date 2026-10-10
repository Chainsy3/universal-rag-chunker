# Changelog

## 0.2.0 — unreleased

- Added optional pypdf, python-docx and openpyxl adapters for PDF/DOCX/XLSX.
- Added schema 1.1 with page, Word body/table and worksheet row/column locators; retained 1.0 validation.
- Preserved all worksheets, formulas as text, merged-cell anchors and nested Word table content.
- Added chunk source locations, extraction hashes, scope-aware coverage and diagnostics.
- Added real-format regressions for corruption, encryption, empty PDF pages and missing dependencies.

## 0.1.0 — unreleased

- Added lossless TXT/Markdown Document IR and source-traceable Chunk Schema.
- Added fixed/recursive strategies, opt-in plugins, TOML configuration and CLI.
- Added deterministic identities, source validation and staged JSON/JSONL exports.
- Added original examples, regression tests, packaging configuration and proposed CI.
