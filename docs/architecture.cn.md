# 架构

[中文](architecture.cn.md) · [English](architecture.en.md)

`Parser → DocumentIR → Validator → Plugin.prepare → Strategy → Plugin.enrich → Finalizer → Validator → RunResult`

调用方选择是否交给 Exporter；CLI 在校验成功后导出。config.py 管配置；registry.py 管显式组件注册；pipeline.py 只协调；models.py 提供类型化数据类；parsers.py、strategies.py、plugins.py 通过 Protocol 描述扩展契约。

没有按 document_type 自动匹配领域策略。组件名不存在、重复注册、显式 parser 与后缀不兼容均失败。第三方代码不自动发现或执行；插件是调用方信任的 Python 代码，不提供隔离沙箱。

office_parsers.py 提供惰性导入的 PDF/DOCX/XLSX 可选适配器。解析器使用同一份原始 bytes 计算 hash 并解析，避免两次读取遇到源文件变化。第三方库版本进入 parser.config_digest，防止库升级改变提取结果但仍复用旧 ID。原文件 hash 与提取文本 hash 分开保存；TXT/Markdown 继续保留原文无损规则。

组件 version 是确定性身份的一部分；升级行为时必须更新组件版本。更改格式字段含义必须更新 schema_version 并提供迁移说明。
