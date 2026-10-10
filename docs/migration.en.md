# Migrating from domain_chunking

[中文](migration.cn.md) · [English](migration.en.md)

Keep the old project as reference; old output cannot be used directly as new IR. The old Document and DocumentStructure become DocumentIR. Old Sections become Blocks with `parent_id` and source locations. Old `content` maps to `text`.

Old UUIDs are not retained. New IDs depend on source content, component versions and configuration, so rebuild downstream indexes. `document_type` no longer forces routing. Automatic textbook-content deletion, railway publisher vocabulary and accident-worksheet filtering are not migrated into the general defaults.

The old CLI is incompatible with the new `urc`. The new version supports PDF/DOCX/XLSX without reproducing railway-specific rules. The old GUI and question-bank rules remain part of the old project.

From 0.1.0 to 0.2.0: new outputs use `schema_version=1.1`, while reading/validation of 1.0 remains supported. Configuration `schema_version` stays 1.0. Package/component version updates change stable IDs and require rebuilding downstream indexes. PDF/Word/Excel require optional extras. Binary `coverage_scope` differs from lossless original text and must not be interpreted as complete original-file recognition.

The bilingual recursive boundary revision is `0.2.0.bilingual.1`. Its changed boundaries and component provenance intentionally change chunk IDs; regenerate affected outputs and indexes.
