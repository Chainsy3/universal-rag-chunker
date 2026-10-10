# Universal RAG Chunker

[中文](README.md) · [Project website](https://Chainsy3.github.io/universal-rag-chunker/) · [Formats](docs/formats.md) · [Issues](https://github.com/Chainsy3/universal-rag-chunker/issues)

Source-traceable, modular document chunking for RAG pipelines. Supports TXT, Markdown, PDF, DOCX and XLSX through a common Python API and CLI, without coupling to an embedding model, vector database or industry vocabulary.

**Version:** 0.2.0 candidate. **Python:** 3.11+. **License:** MIT. Not published to PyPI; install from the source checkout or a locally built wheel.

## Quick start

```sh
git clone https://github.com/Chainsy3/universal-rag-chunker.git
cd universal-rag-chunker
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install ".[all]"
urc chunk examples/guide.md --output out
urc validate out/document.ir.json --chunks out/chunks.jsonl
```

Use the same command for `document.pdf`, `document.docx` or `workbook.xlsx`. Optional dependency groups: `[pdf]`, `[word]`, `[excel]`, `[all]`. The base text/Markdown implementation has no runtime dependencies.

## What it does

| Input | Extraction | Source location |
|---|---|---|
| TXT / Markdown | UTF-8 source, Markdown structure subset | Character offsets |
| PDF | Existing text layer, one block per page | Page number |
| DOCX | Body headings, paragraphs and table rows; nested table text | Body element and row index |
| XLSX | All worksheets, nonempty cells, formulas as text | Worksheet, row, column and cell coordinates |

- Two versioned contracts: **Document IR** for normalized structure, **Chunk Schema** for retrieval units.
- Fixed windows or structure-aware recursive splitting, with character limits and overlap.
- Explicit parser/strategy/plugin registration; plugins are disabled by default.
- Deterministic IDs, reference validation and exact reconstruction of each chunk from IR spans.
- JSON/JSONL export, validation report and manifest; no implicit disk writes from `Pipeline.run()`.

```python
from universal_rag_chunker import Config, Pipeline
from universal_rag_chunker.exporters import export

result = Pipeline().run("document.pdf", Config(), source_id="manual.pdf")
export(result, "out/pdf")
```

Output: `document.ir.json`, `chunks.jsonl`, `report.json`, `manifest.json`. Existing output is protected unless `--overwrite` is explicitly supplied. Directories containing unrelated files are not overwritten.

## Scope and limitations

PDF OCR, legacy `.doc`/`.xls`, complex PDF table reconstruction, images, embedding and GUI processing are not included. DOCX headers, footers, text boxes and revisions are outside extraction scope. XLSX formulas are not calculated, merged cells retain their anchor value, and headers are not guessed. Hidden worksheets are included.

Coverage for binary formats measures **parser-extracted text**, not all visible content in the original file. Character counts are Unicode code points, not model tokens. Markdown parsing is conservative and does not implement all of CommonMark. The website is a project introduction with illustrative examples, not a browser-based file processor.

New outputs use schema **1.1**; validation also supports **1.0**. The independent TOML configuration schema remains 1.0.

## Development

```sh
python -m pip install ".[all]"
python -m unittest discover -s tests -v
python -m compileall -q src
python -m pip install build
python -m build
```

33 tests passed locally on Windows/Python 3.12. CI configuration covers Windows/Linux and Python 3.11–3.13; check actual GitHub Actions results for remote status. See [architecture](docs/architecture.md), [data model](docs/data-model.md), [plugins](docs/plugins.md), [migration](docs/migration.md) and [contributing](CONTRIBUTING.md).

## License

[MIT](LICENSE), Copyright © 2026 Chainsy3. Third-party parser dependencies retain their respective licenses. Examples are original and no private business documents are included.
