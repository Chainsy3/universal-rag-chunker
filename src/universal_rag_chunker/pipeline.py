"""Orchestration with no implicit export or network access."""
from pathlib import Path

from .config import Config
from .models import Chunk, RunResult, VERSION, digest
from .registry import Registry
from .validators import ValidationError, validate_chunks, validate_ir


class ParseError(ValueError):
    pass


class Pipeline:
    def __init__(self, registry=None):
        self.registry = registry or Registry()

    def run(self, source, config=None, *, source_id=None):
        config = config or Config()
        source = Path(source)
        if source.suffix.lower() in (".doc", ".xls"):
            target = ".docx" if source.suffix.lower() == ".doc" else ".xlsx"
            raise ValueError(f"Legacy {source.suffix} is unsupported; save a copy as {target} first")
        strategy = self.registry.resolve("strategies", config.strategy)
        plugins = [self.registry.resolve("plugins", name) for name in config.plugins]
        if config.parser == "auto":
            parsers = [p for p in self.registry.parsers.values() if source.suffix.lower() in p.suffixes]
            if len(parsers) != 1:
                raise ValueError(f"Expected exactly one parser for {source.suffix}")
            parser = parsers[0]
        else:
            parser = self.registry.resolve("parsers", config.parser)
            if source.suffix.lower() not in parser.suffixes:
                raise ValueError("Selected parser is incompatible with file suffix")
        try:
            document = parser.parse(source, source_id or source.name)
        except (OSError, UnicodeError, ValueError) as error:
            raise ParseError(f"{parser.name}: {error}") from error
        validate_ir(document)
        original = document.to_dict()
        for plugin in plugins:
            try:
                document = plugin.prepare(document, config)
                validate_ir(document)
                # V1 plugins may add metadata, but cannot silently rewrite/delete sources.
                require_same = {k: v for k, v in document.to_dict().items() if k != "metadata"}
                if require_same != {k: v for k, v in original.items() if k != "metadata"}:
                    raise ValidationError("V1 prepare may change document metadata only")
            except Exception as error:
                raise ValidationError(f"Plugin {plugin.name}.prepare: {error}") from error
        drafts = strategy.chunk(document, config)
        for plugin in plugins:
            try:
                drafts = plugin.enrich(document, drafts, config)
            except Exception as error:
                raise ValidationError(f"Plugin {plugin.name}.enrich: {error}") from error
        provenance = {"strategy": {"name": strategy.name, "version": strategy.version},
                      "plugins": [{"name": p.name, "version": p.version} for p in plugins],
                      "pipeline_version": VERSION, "config_digest": config.semantic_digest}
        chunks = []
        by_id = {b.block_id: b for b in document.blocks}
        for index, draft in enumerate(drafts):
            # Provide citations directly on chunks as well as through IR references.
            locations = []
            for span in draft.source_spans:
                if span["block_id"] in by_id:
                    locator = dict(by_id[span["block_id"]].locator)
                    if locator not in locations:
                        locations.append(locator)
            draft.metadata["core.source_locations"] = locations
            chunk_id = "chunk_" + digest([document.document_id, draft.text, draft.source_spans, provenance, index])
            chunks.append(Chunk(chunk_id, document.document_id, index, draft.text, draft.kind,
                                draft.heading_path, draft.source_spans, {"characters": len(draft.text)},
                                provenance, draft.metadata, schema_version=document.schema_version))
        report = validate_chunks(document, chunks, config.max_characters)
        return RunResult(document, chunks, report, config.to_dict())
