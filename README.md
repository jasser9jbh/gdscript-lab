# GDScript Lab v1.0.0 — Tauri 2 Application

Production application source and release engineering for **GDScript Lab**.

- Product: GDScript Lab
- Publisher: Journey Beyond Horizons Productions (JBH PRODS)
- Bundle ID: `com.jbhprods.gdscriptlab`
- Version: `1.0.0`
- Corrected frontend SHA-256: `628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336`
- Corrected portable HTML SHA-256: `e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108d`
- COURSE_DATA SHA-256: `c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe`
- Inventory: 27 modules / 171 lessons / 183 code-command blocks / 310 glossary entries / 143 references / 10 projects

## Current release source

The corrected source artifact is the canonical source used for the final native matrix. `src/index.html` and `portable/GDScript_Lab_Godot47_v1.0.0.html` contain byte-identical serialized `COURSE_DATA` at the hash above. The UI maintenance revision embeds the Dreamcatcher SVG, synchronizes light/dark scrollbar chrome, and hardens backup/restore confirmation and validation without changing the curriculum inventory.

The strongest cohesive release validation is `.github/workflows/final-production-release-v7.yml`, proven by GitHub Actions run `33686784014`. The production-safe Android signing path is `.github/workflows/final-android-production-v5-windows.yml`.

For the exact release matrix and remaining blockers, see `RELEASE_STATUS.md`. For the credential-dependent production signing procedure, see `SIGNING_HANDOFF.md`.

### Reproducibility retention note

The validated v7 workflow consumes the corrected source artifact from Actions run `33644641089`. GitHub Actions artifacts are retention-limited, so that run must **not** be treated as permanent source storage. Keep an independently archived copy of the corrected normalized v1.0.0 source package and its SHA-256 alongside release records. The older repository-root source ZIP and reconstruction helpers are historical inputs, not a substitute for the verified corrected source package unless a fresh reconstruction is revalidated against the hashes above.

## Native shell

- Tauri 2 WebView shell for Windows, Linux, macOS, Android and iOS.
- Official Godot/JBH PRODS links open through the Tauri opener plugin.
- Exports use a native Save dialog and native filesystem text write in packaged apps.
- Browser Blob download remains only in the portable/non-Tauri edition.
- Local progress remains local; no account, telemetry, analytics, ad network, updater or automatic HTTP client is added.
- Mobile safe-area handling is included.

## Security model

Capabilities are intentionally narrow: Save dialog, text-file writes to user-selected locations, and system-browser opening for `docs.godotengine.org`, `godotengine.org`, and `jbhprods.com`. No shell plugin, HTTP plugin, updater, broad filesystem-read capability or telemetry is included.

## Pinned release toolchain

- Node.js 22.16.0 in CI
- Rust 1.98.0
- Tauri crate 2.11.5
- Tauri CLI 2.11.4
- tauri-build 2.6.3
- tauri-plugin-fs 2.5.2

## Native validation evidence

Corrected-source native CI has demonstrated:

- Windows x64: NSIS + MSI build and GUI smoke PASS
- Linux x64: AppImage + DEB build and GUI smoke PASS
- macOS Apple Silicon: DMG build
- macOS Intel: DMG build
- Android: APK + AAB compilation reaches completion; production signing is handled separately
- iOS: unsigned native compile PASS; a distributable IPA still requires Apple signing/provisioning

## Android release identity — production rule

A public Android release must use **one persistent owner-controlled signing identity** for v1.0.0 and future direct-distribution updates. CI must never generate a replacement key per run and must never upload a private keystore as a release artifact.

The production-safe Android workflow is `.github/workflows/final-android-production-v5-windows.yml`. It consumes these GitHub Actions secrets when configured:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`
- `ANDROID_STORE_PASSWORD`

When all four are present, APK/AAB are signed and verified. When they are absent, the workflow emits explicitly named `UNSIGNED` outputs rather than pretending the artifacts are production-signed. The private keystore is never uploaded by the workflow.

## Platform signing reality

- Android direct distribution: persistent signing key required for upgrade continuity.
- macOS public distribution: Developer ID signing/notarization is recommended and normally required for a polished Gatekeeper experience.
- iOS public installation: Apple signing/provisioning is required.
- Windows: unsigned installers can function, but Authenticode signing is recommended to reduce reputation/SmartScreen warnings.

## Validation

Inside the corrected source package, run:

```bash
python scripts/check-build-env.py
python scripts/audit.py
```

Release bundles must include regenerated relative-path SHA-256 checksums and must never include private signing keys or passwords.