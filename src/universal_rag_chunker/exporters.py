"""Stage complete validated runs before publishing an output directory."""
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .validators import validate_chunks


def export(result, destination, *, overwrite=False):
    validate_chunks(result.document, result.chunks, result.config["max_characters"])
    destination = Path(destination).absolute()
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {destination.name}; use --overwrite")
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise OSError("Output must be a normal directory")
    if destination.exists():
        allowed = {"document.ir.json", "chunks.json", "chunks.jsonl", "report.json", "manifest.json"}
        names = {p.name for p in destination.iterdir()}
        if names and ("manifest.json" not in names or names - allowed):
            raise OSError("Refusing to replace a directory containing unrelated files")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=".urc-stage-", dir=destination.parent))
    backup = None
    try:
        payloads = {"report.json": json.dumps(result.report, ensure_ascii=False, indent=2)}
        if result.config["include_ir"]:
            payloads["document.ir.json"] = json.dumps(result.document.to_dict(), ensure_ascii=False, indent=2)
        chunks = [c.to_dict() for c in result.chunks]
        if result.config["format"] == "jsonl":
            payloads["chunks.jsonl"] = "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in chunks)
        else:
            payloads["chunks.json"] = json.dumps(chunks, ensure_ascii=False, indent=2)
        hashes = {}
        for name, text in payloads.items():
            raw = text.encode("utf-8")
            (staged / name).write_bytes(raw)
            hashes[name] = hashlib.sha256(raw).hexdigest()
        manifest = {"run_id": uuid4().hex, "created_at": datetime.now(timezone.utc).isoformat(),
                    "source": result.document.source, "parser": result.document.parser,
                    "provenance": result.chunks[0].provenance, "config": result.config, "outputs": hashes}
        (staged / "manifest.json").write_bytes(json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
        if destination.exists():
            backup = destination.with_name(".urc-backup-" + uuid4().hex)
            os.rename(destination, backup)
        try:
            os.rename(staged, destination)
        except OSError:
            if backup:
                os.rename(backup, destination)
                backup = None
            raise
        if backup:
            shutil.rmtree(backup)
        return manifest
    finally:
        if staged.exists():
            shutil.rmtree(staged)
