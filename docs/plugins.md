# 自定义插件

```python
from universal_rag_chunker import Config, Pipeline, Registry

class TagPlugin:
    name = "tag"
    version = "0.1.0"

    def prepare(self, document, config):
        document.metadata["tag.collection"] = "demo"
        return document

    def enrich(self, document, drafts, config):
        for draft in drafts:
            draft.metadata["tag.reviewed"] = True
        return drafts

registry = Registry()
registry.register("plugins", TagPlugin())
result = Pipeline(registry).run("examples/guide.md", Config(plugins=("tag",)))
```

插件按配置顺序运行；默认空列表。prepare 只能修改文档 metadata；enrich 可调整 drafts，但最后仍必须满足来源重建、完整覆盖、顺序与长度约束。不能加入无来源的正文。异常包含插件名称和阶段。

同样可 register("parsers", parser) 或 register("strategies", strategy)。Parser 必须满足当前 Schema 的来源约束：text 保持无损字符分割，page/docx/sheet 使用提取文本 hash 和对应位置。新的来源类型需要先扩展版本化 Schema 与 Validator，不能伪造 text 偏移。默认 Registry 已注册 text/markdown/pdf/docx/xlsx。
