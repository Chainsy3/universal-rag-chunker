# 数据契约 1.1（兼容读取 1.0）

[中文](data-model.cn.md) · [English](data-model.en.md)

DocumentIR 保存 source、parser、blocks、metadata、document_type。每个 block 有唯一 ID、连续 order、parent_id、type、text、locator、attributes。父节点必须是此前出现的 heading，因此不会出现环。heading attributes 包含 level/title。

原始 UTF-8 文件按 Unicode code point 定位，0 起左闭右开。每个 text locator 对应原始字符串片段；不进行换行归一化。所有 block.text 拼接后必须得到原始源文本，hash 必须与 source.content_sha256 一致。UTF-8 BOM 按源字符保留。

二进制格式新增 locator：page 使用 1 起 page；docx 使用 1 起 body_index（正文段落/表格共享序列），表格行另有 1 起 row；sheet 使用 sheet_name、1 起 row、column_start/column_end。表格块 type=table_row，chunk kind=table。正文表格行的 RnCm、Excel 的 A1 等标签属于确定性提取表示，不是原文件中的连续字符偏移。DOCX 嵌套表格文本归入其顶层单元格，不提供嵌套表的独立行列定位。

二进制 source.content_sha256 是原文件 bytes hash；额外 source.extracted_text_sha256 核对 block.text 拼接值。离线 validate 能验证提取文本完整性及来源结构，不能在缺少原文件时证明提取结果等于原文件的全部内容。PDF 空页仍保留空 block 以维持页序号；完全无文本的文件拒绝处理。

Chunk 保存 text、kind、heading_path、source_spans、size、provenance 和 metadata。source_spans 的 start/end 针对 IR block.text，V1 role 只允许 body。所有引用片段按顺序拼接必须精确等于 chunk.text。块级 locator 和局部 span offset 是不同坐标系。

metadata 必须是 JSON 可序列化的有限值；建议领域键使用命名空间，如 exam.question_number，示范插件使用 example.source_name。

SHA-256 计算规则见 models.digest 与 pipeline.py：规范 JSON 使用排序键、紧凑分隔符、UTF-8、不转义非 ASCII 字符。文档 ID 依赖 source_id、源文件 hash、parser 描述；block ID 包含 order、text、定位与结构属性；chunk ID 包含最终文本、来源引用、组件 provenance 和 order。chunk metadata 不参与身份 hash，因此只改显示元数据不代表正文身份改变。

配置 digest 不包括 format/include_ir。路径/时间/run_id 不加入语义配置。validate 命令会核对 ID 与来源内容，不只检查字段形状。

覆盖率是全部非空白 IR 字符中，被至少一个 span 引用的比例。重复 overlap 只计一次；空白字符允许不输出。report.coverage_scope 对文本为 original_text，对二进制格式为 parser_extracted_text。解析诊断会保留在 report.diagnostics。覆盖校验不等同于原文件识别完整率或语义质量评价。
