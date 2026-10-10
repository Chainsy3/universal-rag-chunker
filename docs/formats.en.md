# Format support and source locations

[中文](formats.cn.md) · [English](formats.en.md)

Install all format dependencies with `python -m pip install ".[all]"`. Installing or upgrading with `python -m pip install "universal-rag-chunker[all]"` requires a published package; this source candidate must be installed using a checkout or wheel path.

| Format | Extracted content | Source location | Current limits |
|---|---|---|---|
| TXT/Markdown | Original UTF-8 text and a Markdown structure subset | Zero-based source character offsets | Not a full CommonMark implementation |
| PDF | Existing text layer, split by page | One-based `page` | No OCR, complex layout or table reconstruction; decrypt encrypted files first |
| DOCX | Body paragraphs, headings, tables and nested table text | One-based `body_index` and table `row` | No images, text boxes, headers, footers or revisions; no invented Word page numbers |
| XLSX | Nonempty cells in every worksheet | `sheet_name`, `row`, `column_start/end`; exact coordinates in `attributes.cells` | Formulas preserved as text, not calculated; no guessed headers or charts |

Excel includes hidden worksheets to avoid silent data loss. Merged cells output only the anchor value; merged Word cells avoid duplicate output of the same XML cell. Labels and line breaks in binary formats are normalized parser representations. `coverage=1.0` means all extracted non-whitespace text appears in chunks, not that images or all visible content were parsed.

Each chunk exposes direct locations in `metadata["core.source_locations"]`. If a long row or cell exceeds `max_characters`, multiple chunks may share its row number; `source_spans` further locates slices inside IR text.

PDF pages with no text produce `PDF_PAGE_NO_TEXT` diagnostics. A PDF with no extractable text fails with an OCR hint. Informational diagnostics `DOCX_BODY_SCOPE` and `XLSX_FORMULAS_PRESERVED` explain extraction scope and formula handling.

Legacy `.doc` and `.xls` are unsupported. Save them as `.docx` or `.xlsx` using Word or Excel. Extensions must match the actual format; renaming an extension is not conversion.

Implementation references: [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), [python-docx body-order API](https://python-docx.readthedocs.io/en/latest/api/document.html), [openpyxl workbook reading parameters](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html).
