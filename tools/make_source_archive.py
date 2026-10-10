"""Archive only public project inputs; never include local outputs or environments."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parent / 'universal-rag-chunker-0.2.0-source.zip'
files = [ROOT / name for name in ('pyproject.toml','README.md','README.en.md','CONTRIBUTING.md','CHANGELOG.md','LICENSE','MANIFEST.in','.gitignore')]
for directory in ('src','docs','tests','tools','configs','examples','.github','site'):
    for path in (ROOT / directory).rglob('*'):
        relative = path.relative_to(ROOT)
        if path.is_file() and not any(part == '__pycache__' or part.endswith('.egg-info') for part in relative.parts):
            files.append(path)
with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path,'universal-rag-chunker/'+path.relative_to(ROOT).as_posix())
with ZipFile(OUTPUT) as archive:
    assert archive.testzip() is None
    assert 'universal-rag-chunker/.github/workflows/ci.yml' in archive.namelist()
    print('Verified source archive:',len(archive.namelist()),'files')
