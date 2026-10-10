# 0.2.0 实现与设计的差异

这是独立实现，没有修改 domain_chunking，也没有复制其铁路业务样例。原设计保留在上级 design 目录作为历史提案。

文本解析保留完整原文；0.2.0 已加入 PDF 页码、DOCX 正文与表格行、XLSX 工作表及行列定位，使用 Schema 1.1。二进制 IR 保存实际提取内容，不声称保存原始文件的全部可视内容。

Markdown 使用有限规则解析 ATX 标题、围栏代码与简单列表，不能视为 CommonMark 完整实现。recursive 使用结构 block、换行与句末边界，不是语义模型。短块可合并，但空白分隔块不独立导出，某些跨块空白间隔可能不出现在最终文本；来源 span 仍可精确重建每个输出块。

Validator 是固定的内置阶段；Parser/Strategy/Plugin 可注册。Exporter 目前提供单个 export API 选择 JSON/JSONL；尚未建立第三方 Validator/Exporter 的注册表。没有静态类型检查 CI，当前 CI 使用编译检查、测试、构建及安装后的 CLI 测试。

后续候选：更完整 Markdown 解析、句界可配置、独立 Validator/Exporter Protocol、题库插件、OCR、PDF 表格结构、表头显式配置、旧 DOC/XLS 转换。未实现的能力不属于当前承诺。
