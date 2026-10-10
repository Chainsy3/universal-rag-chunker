# Architecture

[中文](architecture.cn.md) · [English](architecture.en.md)

`Parser → DocumentIR → Validator → Plugin.prepare → Strategy → Plugin.enrich → Finalizer → Validator → RunResult`

The caller decides whether to pass results to the Exporter; the CLI exports after successful validation. `config.py` manages configuration, `registry.py` explicit component registration, `pipeline.py` coordination, and `models.py` typed dataclasses. `parsers.py`, `strategies.py` and `plugins.py` describe extension contracts using Protocols.

There is no automatic domain-strategy selection based on `document_type`. Unknown component names, duplicate registration and an explicit parser incompatible with the file extension cause errors. Third-party code is not automatically discovered or executed. Plugins are Python code trusted by the caller; no isolation sandbox is provided.

`office_parsers.py` provides lazily imported optional PDF/DOCX/XLSX adapters. Parsers hash and parse the same original bytes, avoiding changes between two file reads. Third-party library versions enter `parser.config_digest`, preventing library upgrades from changing extraction results while reusing old IDs. Original-file and extracted-text hashes are stored separately. TXT/Markdown retain their lossless source-text rules.

Component versions participate in deterministic identity; behavior changes require a component version update. Changes to field semantics require a `schema_version` update and migration documentation.
