# Custom plugins

[中文](plugins.cn.md) · [English](plugins.en.md)

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

Plugins run in configuration order; the default list is empty. `prepare` may only change document metadata. `enrich` may adjust drafts, but final results must satisfy source reconstruction, complete non-whitespace coverage, order and length constraints. Source-free body text cannot be added. Errors include the plugin name and stage.

You can also call `register("parsers", parser)` or `register("strategies", strategy)`. Parsers must satisfy the current schema's source constraints: `text` requires lossless character partitioning; `page`/`docx`/`sheet` require the extracted-text hash and corresponding locations. New source types first require extending the versioned Schema and Validator; do not invent text offsets. The default Registry registers `text`, `markdown`, `pdf`, `docx` and `xlsx` parsers.
