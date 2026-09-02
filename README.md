# GDScript Lab v1.0.0 — Tauri 2 Application

Production application source and release engineering for **GDScript Lab**.

- Product: GDScript Lab
- Publisher: Journey Beyond Horizons Productions (JBH PRODS)
- Bundle ID: `com.jbhprods.gdscriptlab`
- Version: `1.0.0`
- Frontend SHA-256: `628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336`
- Portable HTML SHA-256: `e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108d`
- COURSE_DATA SHA-256: `c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe`
- Inventory: 27 modules / 171 lessons / 183 code-command blocks / 310 glossary entries / 143 references / 10 projects

## Canonical release source

The validated application/course payload is represented by the three hashes above. `src/index.html` and `portable/GDScript_Lab_Godot47_v1.0.0.html` contain byte-identical serialized `COURSE_DATA` at the course-data hash above. The UI maintenance revision embeds the Dreamcatcher SVG, synchronizes light/dark scrollbar chrome, and hardens backup/restore confirmation and validation without changing the curriculum inventory.

The normalized production build source used by the final release workflow was generated and validated by GitHub Actions run `33692246998`:

- artifact: `GDScript-Lab-v1.0.0-PRODUCTION-source`
- inner ZIP: `GDScript_Lab_v1.0.0_PRODUCTION_SOURCE.zip`
- SHA-256: `53dd49b8b9ab98de0dd240c6ef31862cd2d04298ed33b7a57562f81269a8f3aa`

The strongest completed unsigned/native cross-platform matrix remains `.github/workflows/final-production-release-v7.yml`, run `33686784014`. The **canonical final public-release path** is now `.github/workflows/final-signed-release.yml`, which requires the normalized production source, independent security/license evidence, platform signing/notarization/provisioning, runtime checks, and final packaging before it can emit a final release.

For the exact platform state and remaining blockers, see `RELEASE_STATUS.md`. For the publisher-credential procedure, see `SIGNING_HANDOFF.md`. For the dependency-security exception record, see `SECURITY_RELEASE_REVIEW.md`.

### Final-pipeline preflight evidence

The hardened final workflow has been registered and executed by GitHub Actions in credential-free push/preflight mode:

- release-branch preflight: run `33695025084` — PASS
- `main` preflight: run `33695098420` — PASS

Those runs proved that the final workflow retrieves the normalized production source, verifies its ZIP/content hashes, reruns the first-party audit, retrieves the independent security/license evidence, and enforces the npm/RustSec/license gates before any platform release work.

The independent public-release security/license workflow also passed on `main` in run `33695098321`, including locked dependency resolution, npm advisory scanning, RustSec scanning, complete `cargo-about` license generation, and the macOS Tauri iOS/App Store Connect CLI probe.

### Reproducibility retention note

The final workflow consumes the normalized production-source Actions artifact from run `33692246998`. GitHub Actions artifacts are retention-limited, so they must **not** be treated as permanent source storage. Keep an owner-controlled private/offline copy of the normalized production-source ZIP and its SHA-256 alongside release records.

A private draft GitHub Release archive of the earlier corrected source also exists as an owner archival copy. Testing showed that the normal workflow token cannot reliably consume that private draft asset, so the final pipeline does not depend on it.

`GDScript_Lab_v1.0.0_Tauri_Production_Project_FINAL.zip` in the repository root is a historical pre-correction build input and is not the canonical final release source.

## Native shell

- Tauri 2 WebView shell for Windows, Linux, macOS, Android and iOS.
- Official Godot/JBH PRODS links open through the Tauri opener plugin.
- Exports use a native Save dialog and native filesystem text write in packaged apps.
- Browser Blob download remains only in the portable/non-Tauri edition.
- Local progress remains local; no account, telemetry, analytics, ad network, updater or automatic HTTP client is added.
- Mobile safe-area handling is included.

## Security model

Capabilities are intentionally narrow: Save dialog, text-file writes to user-selected locations, and system-browser opening for `docs.godotengine.org`, `godotengine.org`, and `jbhprods.com`. No shell plugin, HTTP plugin, updater, broad filesystem-read capability or telemetry is included.

Credential-free release QA reports zero known npm vulnerabilities and zero blocking RustSec vulnerabilities. Current stable Tauri's Linux GTK3 dependency stack carries upstream informational `unsound`/`unmaintained` RustSec warnings; the evaluated release exception is documented in `SECURITY_RELEASE_REVIEW.md`.

## Pinned release toolchain

- Node.js 22.16.0 in CI
- Rust 1.98.0
- Tauri crate 2.11.5
- Tauri CLI 2.11.4
- tauri-build 2.6.3
- tauri-plugin-fs 2.5.2
- Android API 36 / Build Tools 36.0.0 / NDK r29 in the final Android path

## Native validation evidence

Validated native CI has demonstrated:

- Windows x64: NSIS + MSI build and GUI smoke PASS
- Linux x64: AppImage + DEB build and GUI smoke PASS
- macOS Apple Silicon: DMG build PASS
- macOS Intel: DMG build PASS
- Android: APK + AAB compilation PASS; 16 KB and permanent-publisher-signing gates are enforced by the final workflow
- iOS: unsigned native compile PASS; App Store Connect CLI/export surface PASS; final IPA still requires publisher Apple signing/provisioning

The existing all-platform package is therefore a validated **release candidate**, not the universally signed final release.

## Canonical final release workflow

Run `.github/workflows/final-signed-release.yml` manually only after the complete publisher credential set is configured in GitHub Actions secrets/settings.

On ordinary pushes, only its credential-free `pipeline_preflight` runs. The Windows/Linux/macOS/Android/iOS release jobs deliberately execute only on an explicit `workflow_dispatch`.

The manual final workflow requires all of the following before the final package can be assembled:

- Windows: trusted Authenticode identity; application executable, NSIS and MSI signatures must verify `Valid`; signed-app runtime smoke must pass.
- Linux: AppImage + DEB rebuild from the normalized source and AppImage runtime smoke must pass.
- macOS: Developer ID signing and Apple notarization/stapling for Apple Silicon and Intel; codesign, Gatekeeper, stapler and native-architecture launch checks must pass.
- Android: one permanent publisher signing identity; API 36 metadata, 16 KB ZIP/ELF alignment, APK/AAB signature verification and signed-APK Android 15 16 KB emulator smoke must pass.
- iOS: Apple Distribution certificate and matching provisioning profile; the signed App Store Connect IPA must pass codesign/profile verification.

The iOS IPA is an **App Store Connect submission artifact**, not a universal direct-download/sideload installer for arbitrary iPhone/iPad users.

## Android release identity — production rule

A public Android release must use **one persistent owner-controlled signing identity** for v1.0.0 and future updates. CI must never generate a replacement key per run and must never upload a private keystore as a release artifact.

The canonical final workflow consumes these GitHub Actions secrets:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEY_ALIAS`
- `ANDROID_STORE_PASSWORD`
- `ANDROID_KEY_PASSWORD`

Keep the keystore securely outside the public repository and retain it for future updates.

## Final public package policy

Only after every required manual-release job passes does CI assemble:

`GDScript-Lab-v1.0.0-ALL-PLATFORMS-FINAL.zip`

The public package is designed to contain signed/verified platform distributables, the validated portable HTML edition, legal/support/accessibility documentation, third-party notices and complete generated license evidence, release-security/platform-verification evidence, and regenerated SHA-256 checksums.

The proprietary production-source archive is **not** included in the public package. No private signing key, keystore, PFX/P12 private-key file, password, provisioning secret, or Apple API private key belongs in commits, logs, public release assets, or the cross-platform ZIP.

## Validation

Inside the normalized production source package, run:

```bash
python scripts/check-build-env.py
python scripts/audit.py
```

The final credential-gated workflow must complete successfully before `v1.0.0` is described or published as the fully verified public production release.
