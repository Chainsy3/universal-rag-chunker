# 从 domain_chunking 迁移

保留旧项目作为参考，不能直接将旧 output 当作新 IR。旧 Document+DocumentStructure 合并为 DocumentIR；旧 Section 转为带 parent_id 与来源定位的 Block；旧 content 对应新 text。

旧 UUID 不沿用。新 ID 根据源内容、组件版本和配置确定；需要重新构建下游索引。原 document_type 不再强制路由。旧教材的自动删除、铁路出版社词表、事故工作表筛选不会迁入通用默认流程。

旧 CLI 与新 urc 不兼容；新版本已支持 PDF/DOCX/XLSX，但不会复刻旧铁路特定规则。旧 GUI 和题库专用规则仍属于旧项目。

0.1.0 → 0.2.0：新增输出使用 schema_version=1.1，保留读取/验证 1.0；配置 schema_version 仍为 1.0。包/组件版本升级会改变稳定 ID，下游需要重新构建索引。PDF/Word/Excel 需要安装可选 extras。二进制 coverage_scope 与原文无损文本不同，使用时不能直接视为原文件完整识别率。
