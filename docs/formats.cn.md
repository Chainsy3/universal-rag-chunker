# 格式支持与来源定位

[中文](formats.cn.md) · [English](formats.en.md)

安装全部格式依赖：`python -m pip install ".[all]"`。在已安装包的环境升级：`python -m pip install "universal-rag-chunker[all]"` 需要包已经发布，当前本地候选版本请使用目录或 wheel 路径。

| 格式 | 解析内容 | 来源 | 本版边界 |
|---|---|---|---|
| TXT/Markdown | 原始 UTF-8 文本，Markdown 结构子集 | 0 起原文字偏移 | 不提供完整 CommonMark 兼容 |
| PDF | 文本层，按页切分 | 1 起 page | 无 OCR、不还原复杂版式或表格结构；加密文件需先解密 |
| DOCX | 正文段落、标题、表格及嵌套表格文字 | 1 起 body_index，表格 row | 不提取图片、文本框、页眉页脚、修订；不伪造 Word 页码 |
| XLSX | 所有工作表中非空单元格 | sheet_name、row、column_start/end；attributes.cells 保留精确坐标 | 公式保留原文，不计算；不猜测表头；不提取图表 |

Excel 包含隐藏工作表，避免默默丢失数据。合并单元格只输出锚点值；Word 的合并单元格避免重复输出同一个 XML 单元格。二进制格式中的标签/换行是解析器规范化表示，coverage=1.0 仅指这些已提取文字均进入切块，不代表文件中的图片或全部可视内容都被解析。

每个 Chunk 的 `metadata["core.source_locations"]` 给出直接来源。若长行/单元格超出 max_characters，多个 chunk 可能共享同一行号；source_spans 进一步定位到 IR 文本内的片段。

PDF 无文本页会产生 PDF_PAGE_NO_TEXT 诊断；整份 PDF 无可提取文字时失败并提示 OCR。DOCX_BODY_SCOPE 和 XLSX_FORMULAS_PRESERVED 信息诊断解释提取范围和公式模式。

旧 `.doc`、`.xls` 不支持；请在 Word/Excel 中另存为 `.docx`/`.xlsx`。文件后缀必须匹配实际格式，不能仅改扩展名。

实现参考：[pypdf 文本提取](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)、[python-docx 正文顺序 API](https://python-docx.readthedocs.io/en/latest/api/document.html)、[openpyxl 工作簿读取参数](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html)。
