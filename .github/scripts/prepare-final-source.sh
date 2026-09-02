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
(cd "$PROJECT_DIR" && python scripts/audit.py)
