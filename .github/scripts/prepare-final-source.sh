#!/usr/bin/env bash
set -euo pipefail

SOURCE_ZIP="${SOURCE_ZIP:-GDScript_Lab_v1.0.0_Tauri_Production_Project_FINAL.zip}"
SOURCE_GIT_BLOB_SHA1="${SOURCE_GIT_BLOB_SHA1:-43d91956291718bef62f80fb83384316f8e083e9}"
PROJECT_DIR="${PROJECT_DIR:-_incoming/GDScript_Lab_Tauri_v1.0.0}"

test "$(git hash-object "$SOURCE_ZIP")" = "$SOURCE_GIT_BLOB_SHA1"
rm -rf _incoming && mkdir -p _incoming
python -m zipfile -e "$SOURCE_ZIP" _incoming

cat .github/final-transform-chunks/part-*.b64 | tr -d '\r\n' | base64 --decode | gzip -dc > "${RUNNER_TEMP:-/tmp}/gdlab-final-transform.py"
python "${RUNNER_TEMP:-/tmp}/gdlab-final-transform.py" "$PROJECT_DIR"

# First prove the deterministic hardened transform itself is internally valid.
(cd "$PROJECT_DIR" && python scripts/audit.py)

# Apply the two platform-build compatibility pins that were validated against
# the current Tauri 2.11 toolchain. Keep the bundled audit contract in sync so
# the distributed source remains self-auditing after this buildability patch.
python - "$PROJECT_DIR/src-tauri/Cargo.toml" "$PROJECT_DIR/scripts/audit.py" <<'PY'
from pathlib import Path
import sys

cargo_path = Path(sys.argv[1])
audit_path = Path(sys.argv[2])
cargo = cargo_path.read_text(encoding='utf-8')

pins = [
    ('tauri-build', '2.5.6', '2.6.3'),
    ('tauri-plugin-fs', '2.5.1', '2.5.2'),
]
for name, old, new in pins:
    before = f'version = "={old}"'
    after = f'version = "={new}"'
    if after not in cargo:
        if before not in cargo:
            raise SystemExit(f'Expected {name} compatibility pin {old} not found')
        cargo = cargo.replace(before, after, 1)

cargo_path.write_text(cargo, encoding='utf-8')

audit = audit_path.read_text(encoding='utf-8')
for old, new in [('=2.5.6', '=2.6.3'), ('=2.5.1', '=2.5.2')]:
    if old in audit:
        audit = audit.replace(old, new)
audit_path.write_text(audit, encoding='utf-8')
print('Applied validated Tauri compatibility pins and synchronized audit contract')
PY

# Make the source artifact reproducible/buildable on every downstream runner.
# The frontend and course hashes are unaffected by these lockfiles.
(
  cd "$PROJECT_DIR"
  npm install --package-lock-only --ignore-scripts --no-audit --no-fund
  npm ci --ignore-scripts --no-audit --no-fund
)

rustup toolchain install 1.98.0 --profile minimal --no-self-update
(
  cd "$PROJECT_DIR/src-tauri"
  rm -f Cargo.lock
  cargo +1.98.0 generate-lockfile
)
(
  cd "$PROJECT_DIR"
  cargo +1.98.0 metadata --locked --format-version 1 --manifest-path src-tauri/Cargo.toml > /dev/null
  python scripts/audit.py
)

printf '%s\n' 'FINAL BUILDABLE HARDENED SOURCE PASS'
