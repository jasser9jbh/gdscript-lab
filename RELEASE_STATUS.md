# GDScript Lab v1.0.0 — Release Status

Last verified: 2026-09-02

## Canonical validated candidate

The strongest completed native matrix is GitHub Actions run `33686784014` (`GDScript Lab v1.0.0 production candidate v7`). Its validated source revision is represented by these content hashes:

- Frontend `src/index.html`: `628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336`
- Portable HTML: `e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108d`
- Serialized `COURSE_DATA`: `c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe`
- Corrected source ZIP: `dc39f130eb650c08d5b8a3bea1b7a0ef392598fe98dd2af218734db24f2af4e4`

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
| Android | APK, AAB | Build PASS; permanent production signing still needs owner-controlled credentials |
| iOS | Native compile validation | No-sign compile PASS; distributable IPA still needs Apple signing/provisioning |

## Final release automation now prepared

Two workflows define the remaining release path:

- `.github/workflows/archive-verified-source.yml` verifies the corrected source package and stores it as a private **draft GitHub Release** asset under tag `v1.0.0-corrected-source-archive`. This removes dependence on expiring Actions-artifact retention.
- `.github/workflows/final-signed-release.yml` is manual-only and credential-gated. It rebuilds every platform from that durable verified source, performs platform signing/verification, re-runs relevant smoke tests, assembles `GDScript-Lab-v1.0.0-ALL-PLATFORMS-FINAL.zip`, and creates/refreshes a **draft** `v1.0.0` GitHub Release only if every required job succeeds.

The final pipeline deliberately fails rather than emitting a misleading "final" package when required publisher credentials are missing.

## Android final gate

The final workflow uses API 36 / Build Tools 36 / NDK r29, requires 16 KB APK ZIP and native ELF alignment, signs with the permanent owner-controlled release identity, verifies APK/AAB signatures, and smoke-tests the **signed** APK on an Android 15 16 KB emulator.

Required secrets:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEY_ALIAS`
- `ANDROID_STORE_PASSWORD`
- `ANDROID_KEY_PASSWORD`

The same Android signing identity must be retained securely for future direct-distribution updates.

## Windows final gate

Required secrets:

- `WINDOWS_CERTIFICATE_BASE64`
- `WINDOWS_CERTIFICATE_PASSWORD`

Optional repository variable:

- `WINDOWS_TIMESTAMP_URL` — if absent, the final workflow uses `http://timestamp.digicert.com`.

The workflow imports the publisher certificate only into the temporary runner certificate store, lets Tauri Authenticode-sign the build, requires `Get-AuthenticodeSignature` to report `Valid` for both NSIS and MSI, and re-runs the Windows GUI smoke test.

## macOS final gate

For direct-download distribution, use a **Developer ID Application** certificate plus Apple notarization credentials.

Required secrets:

- `MACOS_CERTIFICATE_BASE64`
- `MACOS_CERTIFICATE_PASSWORD`
- `MACOS_KEYCHAIN_PASSWORD`
- `APPLE_API_ISSUER`
- `APPLE_API_KEY`
- `APPLE_API_PRIVATE_KEY_BASE64`

The workflow rebuilds both Apple Silicon and Intel DMGs, requires code-sign verification, Gatekeeper assessment, and a valid stapled notarization ticket.

## iOS final gate

Required secrets:

- `IOS_CERTIFICATE`
- `IOS_CERTIFICATE_PASSWORD`
- `IOS_MOBILE_PROVISION`
- `APPLE_DEVELOPMENT_TEAM`

These represent an Apple Distribution certificate, matching App Store Connect provisioning profile, and the Apple Developer Team ID. The workflow builds with export method `app-store-connect`, requires a generated IPA, validates its embedded signature, and verifies that the provisioning application identifier ends in `com.jbhprods.gdscriptlab`.

## Repository source note

`GDScript_Lab_v1.0.0_Tauri_Production_Project_FINAL.zip` in the repository root is a historical pre-correction packaging/build input used by older workflows. Do not treat that root ZIP alone as proof of the validated source state. The validated source is defined by the corrected source ZIP/content hashes above.

## What remains before calling v1.0.0 universally signed production-ready

Only owner/account-controlled credential work remains:

1. Create or securely select the permanent Android release keystore and add the four Android secrets.
2. Obtain a trusted Windows code-signing certificate and add its PFX/base64 + password secrets.
3. Have an active Apple Developer membership; create/export a Developer ID Application certificate for macOS, create App Store Connect API credentials for notarization, and add the macOS/Apple secrets.
4. Register/confirm the iOS App ID `com.jbhprods.gdscriptlab`, create an Apple Distribution certificate and matching App Store Connect provisioning profile, and add the four iOS secrets.
5. Run `.github/workflows/final-signed-release.yml` and require every job to pass.
6. Review the generated draft `v1.0.0` GitHub Release and final SHA-256 manifest before publishing/distributing it.

No private signing keys, passwords, provisioning secrets, or Apple API private keys belong in commits, logs, public release assets, or the cross-platform ZIP.
