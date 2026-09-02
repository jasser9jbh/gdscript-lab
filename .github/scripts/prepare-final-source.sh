#!/usr/bin/env bash
# Final isolated native release build trigger: 2026-09-02
set -euo pipefail
SOURCE_ZIP="${SOURCE_ZIP:-GDScript_Lab_v1.0.0_Tauri_Production_Project_FINAL.zip}"
SOURCE_GIT_BLOB_SHA1="${SOURCE_GIT_BLOB_SHA1:-43d91956291718bef62f80fb83384316f8e083e9}"
PROJECT_DIR="${PROJECT_DIR:-_incoming/GDScript_Lab_Tauri_v1.0.0}"
test "$(git hash-object "$SOURCE_ZIP")" = "$SOURCE_GIT_BLOB_SHA1"
rm -rf _incoming && mkdir -p _incoming
python -m zipfile -e "$SOURCE_ZIP" _incoming
cat .github/final-transform-chunks/part-*.b64 | tr -d '\r\n' | base64 --decode | gzip -dc > "${RUNNER_TEMP:-/tmp}/gdlab-final-transform.py"
python "${RUNNER_TEMP:-/tmp}/gdlab-final-transform.py" "$PROJECT_DIR"
(cd "$PROJECT_DIR" && python scripts/audit.py)
python - "$PROJECT_DIR/src-tauri/Cargo.toml" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text(encoding='utf-8')
for name,old,new in [('tauri-build','2.5.6','2.6.3'),('tauri-plugin-fs','2.5.1','2.5.2')]:
    before=f'version = "={old}"'
    after=f'version = "={new}"'
    if after in s:
        continue
    if before not in s:
        raise SystemExit(f'Expected {name} compatibility pin {old} not found')
    s=s.replace(before,after,1)
p.write_text(s,encoding='utf-8')
print('Applied validated Tauri build compatibility pins after frozen-source audit')
PY
