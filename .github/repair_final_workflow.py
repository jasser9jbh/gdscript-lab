from pathlib import Path

p = Path(".github/workflows/final-signed-release.yml")
s = p.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    s = s.replace(old, new, 1)

def replace_count(old: str, new: str, expected: int, label: str) -> None:
    global s
    count = s.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} occurrences, found {count}")
    s = s.replace(old, new)

replace_once(
"""on:
  workflow_dispatch:

permissions:
  contents: write
  actions: read

env:
  SOURCE_ARCHIVE_TAG: v1.0.0-corrected-source-archive
  SOURCE_ZIP: GDScript_Lab_v1.0.0_CORRECTED_NATIVE_SOURCE.zip
  SOURCE_ZIP_SHA256: dc39f130eb650c08d5b8a3bea1b7a0ef392598fe98dd2af218734db24f2af4e4
""",
"""on:
  workflow_dispatch:
  push:
    branches:
      - main
      - release/public-preflight-20260902
    paths:
      - '.github/workflows/final-signed-release.yml'

permissions:
  contents: write
  actions: read

env:
  SOURCE_RUN_ID: '33692246998'
  SOURCE_ARTIFACT_NAME: GDScript-Lab-v1.0.0-PRODUCTION-source
  SOURCE_ZIP: GDScript_Lab_v1.0.0_PRODUCTION_SOURCE.zip
  SOURCE_ZIP_SHA256: 53dd49b8b9ab98de0dd240c6ef31862cd2d04298ed33b7a57562f81269a8f3aa
  PREFLIGHT_RUN_ID: '33692316184'
  PREFLIGHT_ARTIFACT_NAME: GDScript-Lab-v1.0.0-PUBLIC-RELEASE-PREFLIGHT
""",
"global source contract",
)

bash_download = """      - name: Download durable verified source archive
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release download "$SOURCE_ARCHIVE_TAG" --repo "$GITHUB_REPOSITORY" --pattern "$SOURCE_ZIP"
"""
bash_artifact = """      - name: Download normalized production source artifact
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.SOURCE_ARTIFACT_NAME }}
          github-token: ${{ github.token }}
          repository: ${{ github.repository }}
          run-id: ${{ env.SOURCE_RUN_ID }}
          path: production-source-artifact
      - name: Resolve normalized production source ZIP
        shell: bash
        run: |
          set -euo pipefail
          FOUND="$(find production-source-artifact -type f -name "$SOURCE_ZIP" -print -quit)"
          test -n "$FOUND"
          cp "$FOUND" "$SOURCE_ZIP"
"""
replace_count(bash_download, bash_artifact, 5, "bash source downloads")

replace_once(
"""      - name: Download durable verified source archive
        shell: pwsh
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh release download $env:SOURCE_ARCHIVE_TAG --repo $env:GITHUB_REPOSITORY --pattern $env:SOURCE_ZIP
""",
"""      - name: Download normalized production source artifact
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.SOURCE_ARTIFACT_NAME }}
          github-token: ${{ github.token }}
          repository: ${{ github.repository }}
          run-id: ${{ env.SOURCE_RUN_ID }}
          path: production-source-artifact
      - name: Resolve normalized production source ZIP
        shell: pwsh
        run: |
          $found=Get-ChildItem production-source-artifact -Recurse -File -Filter $env:SOURCE_ZIP | Select-Object -First 1
          if (-not $found) { throw 'Normalized production source ZIP not found in artifact' }
          Copy-Item $found.FullName $env:SOURCE_ZIP
""",
"Windows source download",
)

replace_once(
"""jobs:
  linux:
""",
"""jobs:
  pipeline_preflight:
    name: Final release pipeline preflight
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - name: Download normalized production source artifact
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.SOURCE_ARTIFACT_NAME }}
          github-token: ${{ github.token }}
          repository: ${{ github.repository }}
          run-id: ${{ env.SOURCE_RUN_ID }}
          path: production-source-artifact
      - name: Verify normalized source archive
        shell: bash
        run: |
          set -euo pipefail
          FOUND="$(find production-source-artifact -type f -name "$SOURCE_ZIP" -print -quit)"
          test -n "$FOUND"
          test "$(sha256sum "$FOUND" | awk '{print $1}')" = "$SOURCE_ZIP_SHA256"
          rm -rf "$RUNNER_TEMP/source-check"; mkdir -p "$RUNNER_TEMP/source-check"
          python -m zipfile -e "$FOUND" "$RUNNER_TEMP/source-check"
          test "$(sha256sum "$RUNNER_TEMP/source-check/$PROJECT_DIR/src/index.html" | awk '{print $1}')" = "$EXPECTED_FRONTEND_SHA256"
          test "$(sha256sum "$RUNNER_TEMP/source-check/$PROJECT_DIR/portable/GDScript_Lab_Godot47_v1.0.0.html" | awk '{print $1}')" = "$EXPECTED_PORTABLE_SHA256"
          cd "$RUNNER_TEMP/source-check/$PROJECT_DIR"
          python scripts/no_unicode_dashes_check.py
          python scripts/audit.py | tee "$RUNNER_TEMP/final-source-audit.txt"
          grep -q "$EXPECTED_COURSE_SHA256" "$RUNNER_TEMP/final-source-audit.txt"
      - name: Download security and license preflight evidence
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.PREFLIGHT_ARTIFACT_NAME }}
          github-token: ${{ github.token }}
          repository: ${{ github.repository }}
          run-id: ${{ env.PREFLIGHT_RUN_ID }}
          path: preflight-evidence
      - name: Require passing security/license evidence
        shell: bash
        run: |
          set -euo pipefail
          REPORT="$(find preflight-evidence -type f -name PUBLIC_RELEASE_PREFLIGHT.txt -print -quit)"
          LICENSES="$(find preflight-evidence -type f -name THIRD_PARTY_LICENSES.html -print -quit)"
          NPM="$(find preflight-evidence -type f -name NPM_AUDIT.json -print -quit)"
          CARGO="$(find preflight-evidence -type f -name CARGO_AUDIT.json -print -quit)"
          test -s "$REPORT" && test -s "$LICENSES" && test -s "$NPM" && test -s "$CARGO"
          grep -q 'npm audit moderate-or-higher gate exit: 0' "$REPORT"
          grep -q 'RustSec cargo-audit gate exit: 0' "$REPORT"
          printf '%s\n' 'PASS: source, dependency advisory and third-party license gates are available and verified.'

  linux:
    needs: pipeline_preflight
    if: ${{ github.event_name == 'workflow_dispatch' }}
""",
"pipeline preflight insertion",
)

for job in ("windows", "macos", "android", "ios"):
    replace_once(
        f"  {job}:\n",
        f"  {job}:\n    needs: pipeline_preflight\n    if: ${{{{ github.event_name == 'workflow_dispatch' }}}}\n",
        f"{job} dispatch gate",
    )

replace_once(
"""          $app=Get-ChildItem src-tauri/target -Recurse -File -Filter gdscript-lab.exe | Where-Object { $_.FullName -match '\\\\release\\\\gdscript-lab\\.exe$' } | Select-Object -First 1
          $p=Start-Process $app.FullName -PassThru; Start-Sleep 10
""",
"""          $app=Get-ChildItem src-tauri/target -Recurse -File -Filter gdscript-lab.exe | Where-Object { $_.FullName -match '\\\\release\\\\gdscript-lab\\.exe$' } | Select-Object -First 1
          if (-not $app) { throw 'Signed application executable not found' }
          $appSig=Get-AuthenticodeSignature $app.FullName
          if ($appSig.Status -ne 'Valid') { throw "Authenticode verification failed for application executable: $($appSig.Status)" }
          $p=Start-Process $app.FullName -PassThru; Start-Sleep 10
""",
"Windows executable signature verification",
)

replace_once(
"""          Get-AuthenticodeSignature "$out\\GDScript-Lab-v1.0.0-Setup.exe","$out\\GDScript-Lab-v1.0.0.msi" | Format-List * | Out-File "$out\\AUTHENTICODE_VERIFICATION.txt"
""",
"""          Get-AuthenticodeSignature $app.FullName,"$out\\GDScript-Lab-v1.0.0-Setup.exe","$out\\GDScript-Lab-v1.0.0.msi" | Format-List * | Out-File "$out\\AUTHENTICODE_VERIFICATION.txt"
""",
"Windows signature evidence",
)

replace_once(
"""          - { arch: Apple-Silicon, target: aarch64-apple-darwin }
          - { arch: Intel, target: x86_64-apple-darwin }
    runs-on: macos-latest
""",
"""          - { arch: Apple-Silicon, target: aarch64-apple-darwin, os: macos-15 }
          - { arch: Intel, target: x86_64-apple-darwin, os: macos-15-intel }
    runs-on: ${{ matrix.os }}
""",
"macOS native runner matrix",
)

replace_once(
"""          xcrun stapler validate "$APP"
          codesign --verify --verbose=2 "$DMG"
          OUT="$RUNNER_TEMP/macos-final"; mkdir -p "$OUT"
""",
"""          xcrun stapler validate "$APP"
          codesign --verify --verbose=2 "$DMG"
          APP_EXEC="$(find "$APP/Contents/MacOS" -maxdepth 1 -type f -print -quit)"
          test -n "$APP_EXEC" && test -x "$APP_EXEC"
          "$APP_EXEC" > "$RUNNER_TEMP/macos-smoke.log" 2>&1 & PID=$!
          sleep 10
          if ! kill -0 "$PID" 2>/dev/null; then
            wait "$PID" || true
            cat "$RUNNER_TEMP/macos-smoke.log" || true
            exit 1
          fi
          kill "$PID" || true
          wait "$PID" || true
          OUT="$RUNNER_TEMP/macos-final"; mkdir -p "$OUT"
""",
"macOS runtime smoke",
)

replace_once(
"""          xcrun stapler validate "$APP" > "$OUT/NOTARIZATION_STAPLE_VERIFICATION.txt" 2>&1
          shasum -a 256 "$OUT"/* > "$OUT/SHA256SUMS.txt"
""",
"""          xcrun stapler validate "$APP" > "$OUT/NOTARIZATION_STAPLE_VERIFICATION.txt" 2>&1
          printf '%s\\n' 'PASS: signed/notarized macOS app launched on its native-architecture runner.' > "$OUT/MACOS_RUNTIME_VERIFICATION.txt"
          shasum -a 256 "$OUT"/* > "$OUT/SHA256SUMS.txt"
""",
"macOS runtime evidence",
)

replace_once(
"""      - run: brew install cocoapods
      - name: Build signed IPA for App Store Connect
""",
"""      - run: brew install cocoapods
      - name: Import iOS distribution certificate and provisioning profile
        shell: bash
        env:
          IOS_CERTIFICATE: ${{ secrets.IOS_CERTIFICATE }}
          IOS_CERTIFICATE_PASSWORD: ${{ secrets.IOS_CERTIFICATE_PASSWORD }}
          IOS_MOBILE_PROVISION: ${{ secrets.IOS_MOBILE_PROVISION }}
          APPLE_DEVELOPMENT_TEAM: ${{ secrets.APPLE_DEVELOPMENT_TEAM }}
        run: |
          set -euo pipefail
          python - <<'PY'
          import base64, os, pathlib
          temp=pathlib.Path(os.environ['RUNNER_TEMP'])
          temp.joinpath('ios-distribution.p12').write_bytes(base64.b64decode(os.environ['IOS_CERTIFICATE']))
          temp.joinpath('gdscript-lab.mobileprovision').write_bytes(base64.b64decode(os.environ['IOS_MOBILE_PROVISION']))
          PY
          KEYCHAIN="$RUNNER_TEMP/gdlab-ios.keychain-db"
          KEYCHAIN_PASSWORD="$(python - <<'PY'
          import secrets
          print(secrets.token_urlsafe(32))
          PY
          )"
          security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN"
          security default-keychain -s "$KEYCHAIN"
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN"
          security set-keychain-settings -t 3600 -u "$KEYCHAIN"
          security import "$RUNNER_TEMP/ios-distribution.p12" -k "$KEYCHAIN" -P "$IOS_CERTIFICATE_PASSWORD" -T /usr/bin/codesign
          security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN"
          PROFILE_PLIST="$RUNNER_TEMP/ios-profile.plist"
          security cms -D -i "$RUNNER_TEMP/gdscript-lab.mobileprovision" > "$PROFILE_PLIST"
          UUID="$(/usr/libexec/PlistBuddy -c 'Print :UUID' "$PROFILE_PLIST")"
          TEAM="$(/usr/libexec/PlistBuddy -c 'Print :TeamIdentifier:0' "$PROFILE_PLIST")"
          PROFILE_APP_ID="$(/usr/libexec/PlistBuddy -c 'Print :Entitlements:application-identifier' "$PROFILE_PLIST")"
          test "$TEAM" = "$APPLE_DEVELOPMENT_TEAM" || { echo "Provisioning team mismatch: $TEAM" >&2; exit 1; }
          case "$PROFILE_APP_ID" in
            "$APPLE_DEVELOPMENT_TEAM.com.jbhprods.gdscriptlab"|*.com.jbhprods.gdscriptlab) ;;
            *) echo "Provisioning profile application identifier mismatch: $PROFILE_APP_ID" >&2; exit 1;;
          esac
          mkdir -p "$HOME/Library/MobileDevice/Provisioning Profiles"
          cp "$RUNNER_TEMP/gdscript-lab.mobileprovision" "$HOME/Library/MobileDevice/Provisioning Profiles/$UUID.mobileprovision"
          IDENTITY="$(security find-identity -v -p codesigning "$KEYCHAIN" | sed -n 's/.*"\\(Apple Distribution:.*\\)".*/\\1/p' | head -1)"
          test -n "$IDENTITY" || { security find-identity -v -p codesigning "$KEYCHAIN"; echo 'Apple Distribution identity not found.' >&2; exit 1; }
          echo "APPLE_SIGNING_IDENTITY=$IDENTITY" >> "$GITHUB_ENV"
          echo "IOS_PROFILE_UUID=$UUID" >> "$GITHUB_ENV"
          rm -f "$RUNNER_TEMP/ios-distribution.p12"
      - name: Build signed IPA for App Store Connect
""",
"iOS signing material import",
)

replace_once(
"""  package:
    name: Assemble final all-platform signed release
    needs: [linux, windows, macos, android, ios]
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/download-artifact@v4
""",
"""  package:
    name: Assemble final all-platform verified release
    needs: [linux, windows, macos, android, ios]
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
""",
"package checkout",
)

replace_once(
"""      - name: Assemble final package
        shell: bash
""",
"""      - name: Download public-release security/license evidence
        uses: actions/download-artifact@v4
        with:
          name: ${{ env.PREFLIGHT_ARTIFACT_NAME }}
          github-token: ${{ github.token }}
          repository: ${{ github.repository }}
          run-id: ${{ env.PREFLIGHT_RUN_ID }}
          path: preflight-evidence
      - name: Assemble final package
        shell: bash
""",
"package security evidence",
)

replace_once(
"""          mkdir -p "$ROOT/Windows" "$ROOT/Linux" "$ROOT/macOS/Intel" "$ROOT/macOS/Apple-Silicon" "$ROOT/Android" "$ROOT/iOS" "$ROOT/Source"
""",
"""          mkdir -p "$ROOT/Windows" "$ROOT/Linux" "$ROOT/macOS/Intel" "$ROOT/macOS/Apple-Silicon" "$ROOT/Android" "$ROOT/iOS" "$ROOT/Portable" "$ROOT/Documentation"
""",
"public package directories",
)

replace_once(
"""          cp "$SOURCE_ZIP" "$ROOT/Source/GDScript-Lab-v1.0.0-source.zip"
          find artifacts -type f \\( -name '*VERIFICATION.txt' -o -name '*IDENTITY.txt' -o -name '*BADGING.txt' \\) -exec cp {} "$ROOT/" \\;
""",
"""          rm -rf source-public-metadata && mkdir -p source-public-metadata
          unzip -q "$SOURCE_ZIP" -d source-public-metadata
          SRCROOT="source-public-metadata/$PROJECT_DIR"
          test -f "$SRCROOT/LICENSE.txt" && cp "$SRCROOT/LICENSE.txt" "$ROOT/LICENSE.txt"
          test -f "$SRCROOT/THIRD_PARTY_NOTICES.md" && cp "$SRCROOT/THIRD_PARTY_NOTICES.md" "$ROOT/THIRD_PARTY_NOTICES.md"
          for f in PRIVACY.md TERMS.md ACCESSIBILITY.md SUPPORT.md README_DISTRIBUTION.md; do
            test -f "$SRCROOT/$f" && cp "$SRCROOT/$f" "$ROOT/Documentation/$f"
          done
          cp "$SRCROOT/portable/GDScript_Lab_Godot47_v1.0.0.html" "$ROOT/Portable/GDScript_Lab_Godot47_v1.0.0.html"
          LICENSE_REPORT="$(find preflight-evidence -type f -name THIRD_PARTY_LICENSES.html -print -quit)"
          PREFLIGHT_REPORT="$(find preflight-evidence -type f -name PUBLIC_RELEASE_PREFLIGHT.txt -print -quit)"
          NPM_AUDIT="$(find preflight-evidence -type f -name NPM_AUDIT.json -print -quit)"
          CARGO_AUDIT="$(find preflight-evidence -type f -name CARGO_AUDIT.json -print -quit)"
          test -n "$LICENSE_REPORT" && cp "$LICENSE_REPORT" "$ROOT/THIRD_PARTY_LICENSES.html"
          test -n "$PREFLIGHT_REPORT" && cp "$PREFLIGHT_REPORT" "$ROOT/Documentation/PUBLIC_RELEASE_PREFLIGHT.txt"
          test -n "$NPM_AUDIT" && cp "$NPM_AUDIT" "$ROOT/Documentation/NPM_AUDIT.json"
          test -n "$CARGO_AUDIT" && cp "$CARGO_AUDIT" "$ROOT/Documentation/CARGO_AUDIT.json"
          test -f SECURITY_RELEASE_REVIEW.md && cp SECURITY_RELEASE_REVIEW.md "$ROOT/Documentation/SECURITY_RELEASE_REVIEW.md"
          find artifacts -type f \\( -name '*VERIFICATION.txt' -o -name '*IDENTITY.txt' -o -name '*BADGING.txt' \\) -exec cp {} "$ROOT/" \\;
""",
"private-source removal/public evidence",
)

s = s.replace(
    "          macOS: Developer ID-signed and Apple-notarized/stapled DMGs for Apple Silicon and Intel.\n",
    "          macOS: DMGs containing Developer ID-signed, Apple-notarized/stapled apps for Apple Silicon and Intel; native-architecture launch smoke required by CI.\n",
)
s = s.replace(
    "          iOS: Apple-distribution-signed App Store Connect IPA with provisioning identifier verification.\n",
    "          iOS: Apple-distribution-signed App Store Connect submission IPA with provisioning identifier verification; this is not a universal direct-download iOS installer.\n",
)
s = s.replace(
    "          No private signing key, certificate password, provisioning secret, or Apple API private key is included.\n",
    "          Portable: self-contained validated HTML edition included for browser/offline use.\n"
    "          Proprietary build source: NOT included in the public package.\n"
    "          Full third-party license report and security preflight evidence: included.\n\n"
    "          No private signing key, certificate password, provisioning secret, or Apple API private key is included.\n",
)
s = s.replace(
    "          Corrected source ZIP SHA-256: ${SOURCE_ZIP_SHA256}\n",
    "          Internal production build-source ZIP SHA-256: ${SOURCE_ZIP_SHA256}\n"
    "          Internal source artifact run: ${SOURCE_RUN_ID}\n"
    "          Security/license preflight run: ${PREFLIGHT_RUN_ID}\n"
    "          Public proprietary source archive included: NO\n",
)
s = s.replace(
    "          Release class: FINAL SIGNED CROSS-PLATFORM\n",
    "          Release class: FINAL VERIFIED CROSS-PLATFORM\n",
)
s = s.replace(
    "--notes 'Final signed cross-platform package produced only after all platform signing and verification jobs passed. Review the attached manifest/checksums before publishing this draft release.' --draft",
    "--notes 'Final verified cross-platform package produced only after all required platform signing, notarization/provisioning, runtime, security and license gates passed. The iOS IPA is an App Store Connect submission artifact rather than a universal direct-download installer. Review the attached manifest/checksums before publishing this draft release.' --draft",
)

required = [
    "SOURCE_RUN_ID: '33692246998'",
    "pipeline_preflight:",
    "macos-15-intel",
    "Import iOS distribution certificate and provisioning profile",
    "THIRD_PARTY_LICENSES.html",
    "Public proprietary source archive included: NO",
    "Release class: FINAL VERIFIED CROSS-PLATFORM",
]
for token in required:
    if token not in s:
        raise SystemExit(f"required final invariant missing: {token}")
for forbidden in ("SOURCE_ARCHIVE_TAG", "gh release download", "GDScript_Lab_v1.0.0_CORRECTED_NATIVE_SOURCE.zip"):
    if forbidden in s:
        raise SystemExit(f"obsolete release token remains: {forbidden}")

p.write_text(s, encoding="utf-8")
print("PASS: final-signed-release.yml hardened")
