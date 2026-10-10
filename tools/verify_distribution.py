"""Offline build, isolated target installation, and installed-package smoke test."""
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
from setuptools.build_meta import build_sdist, build_wheel

DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)
sdist = build_sdist(str(DIST))
wheel = build_wheel(str(DIST))
with zipfile.ZipFile(DIST / wheel) as archive:
    assert len([p for p in archive.namelist() if p.endswith('.schema.json')]) == 4

target = ROOT / '.verification' / 'installed-0.2.0'
subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', '--no-index', '--upgrade',
                '--target', str(target), str(DIST / wheel)], check=True)
env = dict(os.environ, PYTHONPATH=str(target), PYTHONUTF8='1')
work = ROOT / '.verification'
output = work / 'smoke-output-0.2.0'
subprocess.run([sys.executable, '-m', 'universal_rag_chunker', 'chunk', str(ROOT / 'examples/guide.md'),
                '--config', str(ROOT / 'configs/default.toml'), '--output', str(output), '--overwrite'],
               cwd=work, env=env, check=True)
subprocess.run([sys.executable, '-m', 'universal_rag_chunker', 'validate', str(output / 'document.ir.json'),
                '--chunks', str(output / 'chunks.jsonl')], cwd=work, env=env, check=True)
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'],
               cwd=work, env=env, check=True)
print('VERIFIED:', wheel, sdist)
