# Verification record — 0.2.0

[中文](verification.cn.md) · [English](verification.en.md)

Date: 2026-10-10. Local environment: Windows, Python 3.12.14.

- The initial 33 unittest cases passed without skips, covering text parsing, configuration, source/identity, determinism, lengths, plugins, CLI, export failures, overwrite protection and real PDF/DOCX/XLSX parsing.
- Wheel and sdist were built using locally available setuptools, without downloading build dependencies.
- The wheel was installed into a separate project-local verification directory without changing system Python.
- Tests ran against the installed package from a separate working directory, including the chunk → validate CLI round trip.
- The original `guide.md` example produced 5 chunks, with a maximum of 136 characters and 100% non-whitespace source-character coverage in the initial verification.
- PDF tests cover multiple pages, empty-page diagnostics, textless/encrypted/corrupt files, page locations and long-text export/validation.
- Word tests cover Chinese headings, original body/table order, merged cells, nested tables and CLI export/validation.
- Excel tests cover all worksheets, hidden sheets, two-column/single-column tables, merged cells, dates, zero/False values, formula text, empty rows and long cells.
- Schema 1.1 is verified while retaining export/validation tests for Schema 1.0.
- Local format dependencies were pypdf 6.10.0, python-docx 1.2.0 and openpyxl 3.1.5. No dependencies were downloaded for local verification. The separate install directory isolated the project package while using format dependencies from the runtime.

The bilingual boundary update passed 36 local tests, including Chinese sentences without spaces, English words/closing quotes, and mixed-content source integrity and determinism. All six GitHub Actions jobs passed on Windows/Linux with Python 3.11, 3.12 and 3.13: [bilingual-update CI run](https://github.com/Chainsy3/universal-rag-chunker/actions/runs/38021558746). The system-default Python 3.9 does not meet project requirements; local verification used the application's bundled Python 3.12.

These results verify engineering invariants. They do not constitute retrieval-quality benchmarks or full Markdown conformance certification. Documentation-only updates are checked for language pairs and link integrity rather than treated as new algorithm evaluations.
