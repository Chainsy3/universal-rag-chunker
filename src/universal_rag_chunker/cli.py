"""Stable CLI exit codes: config=2, parse=3, validation=4, export=5."""
import argparse
import json
import sys
from pathlib import Path

from .config import Config
from .exporters import export
from .models import Chunk, DocumentIR
from .pipeline import ParseError, Pipeline
from .registry import Registry
from .validators import ValidationError, validate_chunks, validate_ir


def main(argv=None):
    parser = argparse.ArgumentParser(prog="urc", description="Traceable TXT/Markdown/PDF/DOCX/XLSX chunking")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("chunk")
    run.add_argument("input", type=Path)
    run.add_argument("--config", type=Path)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--strategy")
    run.add_argument("--parser")
    run.add_argument("--source-id")
    run.add_argument("--max-characters", type=int)
    run.add_argument("--minimum-characters", type=int)
    run.add_argument("--overlap-characters", type=int)
    run.add_argument("--format", choices=("json", "jsonl"))
    run.add_argument("--overwrite", action="store_true")
    validate = sub.add_parser("validate")
    validate.add_argument("document", type=Path)
    validate.add_argument("--chunks", type=Path)
    validate.add_argument("--max-characters", type=int, default=1200)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("document", type=Path)
    sub.add_parser("list-components")
    args = parser.parse_args(argv)
    if args.command == "list-components":
        registry = Registry()
        print(json.dumps({kind: sorted(getattr(registry, kind)) for kind in ("parsers", "strategies", "plugins")}))
        return 0
    if args.command != "chunk":
        try:
            document = DocumentIR.from_dict(json.loads(args.document.read_text(encoding="utf-8")))
            validate_ir(document)
            if args.command == "validate" and args.chunks:
                text = args.chunks.read_text(encoding="utf-8")
                data = ([json.loads(line) for line in text.splitlines() if line.strip()]
                        if args.chunks.suffix == ".jsonl" else json.loads(text))
                report = validate_chunks(document, [Chunk(**v) for v in data], args.max_characters)
            else:
                report = {"valid": True, "document_id": document.document_id, "block_count": len(document.blocks)}
            print(json.dumps(report, ensure_ascii=False))
            return 0
        except (ValueError, OSError, TypeError, KeyError) as error:
            print(f"Validation: {error}", file=sys.stderr)
            return 4
    try:
        config = Config.load(args.config, **{key: getattr(args, key) for key in
                             ("parser", "strategy", "max_characters", "minimum_characters", "overlap_characters", "format")})
        result = Pipeline().run(args.input, config, source_id=args.source_id)
    except ParseError as error:
        print(f"Parse: {error}", file=sys.stderr)
        return 3
    except ValidationError as error:
        print(f"Validation: {error}", file=sys.stderr)
        return 4
    except (ValueError, OSError, TypeError) as error:
        print(f"Configuration: {error}", file=sys.stderr)
        return 2
    try:
        export(result, args.output, overwrite=args.overwrite)
    except (OSError, ValueError) as error:
        print(f"Export: {error}", file=sys.stderr)
        return 5
    print(json.dumps(result.report, ensure_ascii=False))
    return 0
