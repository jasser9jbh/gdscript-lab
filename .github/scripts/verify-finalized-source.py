#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, subprocess, sys, zipfile

SOURCE_ZIP = 'GDScript_Lab_v1.0.0_PRODUCTION_FINALIZED_SOURCE.zip'
SOURCE_SHA256 = 'c418540f7ef9a00783b44751d3316e37a57e1c486fb071c0136d0fca5d7b1527'
PROJECT_DIR = 'GDScript_Lab_Tauri_v1.0.0'
FRONTEND_SHA256 = '628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336'
PORTABLE_SHA256 = 'e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108d'
COURSE_SHA256 = 'c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe'

def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit('usage: verify-finalized-source.py <artifact-dir> <extract-dir>')
    artifact_dir = pathlib.Path(sys.argv[1])
    extract_dir = pathlib.Path(sys.argv[2])
    matches = list(artifact_dir.rglob(SOURCE_ZIP))
    if len(matches) != 1:
        raise SystemExit(f'expected exactly one {SOURCE_ZIP}, found {len(matches)}')
    source_zip = matches[0]
    actual = sha(source_zip)
    if actual != SOURCE_SHA256:
        raise SystemExit(f'finalized source SHA-256 mismatch: {actual}')
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source_zip) as zf:
        zf.extractall(extract_dir)
    project = extract_dir / PROJECT_DIR
    frontend = project / 'src' / 'index.html'
    portable = project / 'portable' / 'GDScript_Lab_Godot47_v1.0.0.html'
    if sha(frontend) != FRONTEND_SHA256:
        raise SystemExit('frontend SHA-256 mismatch')
    if sha(portable) != PORTABLE_SHA256:
        raise SystemExit('portable SHA-256 mismatch')
    cfg = json.loads((project / 'src-tauri' / 'tauri.conf.json').read_text(encoding='utf-8'))
    bundle = cfg['bundle']
    android = bundle['android']
    ios = bundle['iOS']
    if android.get('versionCode') != 1000000 or android.get('autoIncrementVersionCode') is not False:
        raise SystemExit('Android release version policy mismatch')
    if str(ios.get('minimumSystemVersion')) != '15.0' or str(ios.get('bundleVersion')) != '1':
        raise SystemExit('iOS release version/deployment policy mismatch')
    cargo_cfg = (project / '.cargo' / 'config.toml').read_text(encoding='utf-8')
    for required in ('max-page-size=16384', 'common-page-size=16384'):
        if required not in cargo_cfg:
            raise SystemExit(f'missing Android 16-KB linker policy: {required}')
    audit = subprocess.run([sys.executable, 'scripts/audit.py'], cwd=project, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.write(audit.stdout)
    if audit.returncode:
        raise SystemExit('source audit failed')
    if COURSE_SHA256 not in audit.stdout:
        raise SystemExit('expected COURSE_DATA hash missing from audit')
    print(f'PASS: exact production-finalized source verified: {SOURCE_SHA256}')

if __name__ == '__main__':
    main()
