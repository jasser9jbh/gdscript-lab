# GDScript Lab v1.0.0 — Release Status

Last verified: 2026-09-02

## Canonical validated candidate

The strongest completed native matrix is GitHub Actions run `33686784014` (`GDScript Lab v1.0.0 production candidate v7`). Its validated source revision is represented by these content hashes:

- Frontend `src/index.html`: `628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336`
- Portable HTML: `e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108abe`
- Serialized `COURSE_DATA`: `c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe`

Verified inventory:

- 27 modules
- 171 lessons
- 183 code/command blocks
- 310 glossary entries
- 143 reference entries
- 10 projects

The all-platform release-candidate ZIP assembled by that run has SHA-256:

`994b7e885727b637a8ed71ed72369010ecd7d849fbcdce7e330cfce5d3fde34d`

## Platform matrix

| Platform | Artifact class | Verified state |
| --- | --- | --- |
| Windows x64 | NSIS `.exe`, MSI | Build PASS; GUI smoke PASS; Authenticode not asserted |
| Linux x64 | AppImage, DEB | Build PASS; GUI smoke PASS |
| macOS Apple Silicon | DMG | Build PASS; signing/notarization not asserted |
| macOS Intel | DMG | Build PASS; signing/notarization not asserted |
| Android | APK, AAB | Build PASS; production signing pending owner-controlled credentials |
| iOS | Native compile validation | No-sign compile PASS; distributable IPA requires Apple signing/provisioning |

## Android signing rule

A public Android release must use one persistent owner-controlled signing identity for v1.0.0 and future updates. Never generate a replacement release key per CI run and never publish or upload a private keystore as a release artifact.

The production-safe workflow is `.github/workflows/final-android-production-v5-windows.yml` and expects:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEY_ALIAS`
- `ANDROID_STORE_PASSWORD`
- `ANDROID_KEY_PASSWORD`

If those secrets are unavailable, outputs must remain explicitly `UNSIGNED`.

## Repository source note

`GDScript_Lab_v1.0.0_Tauri_Production_Project_FINAL.zip` in the repository root is a historical pre-correction packaging/build input used by older workflows. Do not treat that root ZIP alone as proof of the validated v7 source state. The validated candidate is defined by the hashes above and the corrected-source/native-matrix evidence.

## What remains before calling v1.0.0 fully signed production-ready

1. Configure the permanent Android signing identity and rebuild/verify signed APK + AAB.
2. Sign and notarize both macOS builds with the publisher's Apple Developer credentials if distributing as a polished public macOS release.
3. Build/sign/provision a distributable iOS IPA with the publisher's Apple Developer credentials.
4. Authenticode-sign the Windows installers if a polished public Windows trust experience is required.
5. Recompute and publish final SHA-256 checksums after signing because signatures change artifact bytes.

Until those external credential-dependent operations are complete, the current all-platform package is correctly classified as a release candidate rather than a universally signed final release.
