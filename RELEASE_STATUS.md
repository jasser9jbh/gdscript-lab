# GDScript Lab v1.0.0 — Release Status

Last verified: 2026-09-03

## Canonical product state

The validated application/course payload remains unchanged and is identified by these hashes:

- Frontend `src/index.html`: `628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336`
- Portable HTML: `e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108d`
- Serialized `COURSE_DATA`: `c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe`

Verified inventory:

- 27 modules
- 171 lessons
- 183 code/command blocks
- 310 glossary entries
- 143 reference entries
- 10 projects

The strongest completed unsigned/native matrix remains GitHub Actions run `33686784014` (`GDScript Lab v1.0.0 production candidate v7`). Its all-platform RC ZIP has SHA-256:

`994b7e885727b637a8ed71ed72369010ecd7d849fbcdce7e330cfce5d3fde34d`

That RC is a validated release candidate, **not** the universally signed final public release.

## Production source and public-release preflight

The normalized production build source was generated and validated by Actions run `33692246998` as artifact:

`GDScript-Lab-v1.0.0-PRODUCTION-source`

Inner production-source ZIP:

`GDScript_Lab_v1.0.0_PRODUCTION_SOURCE.zip`

SHA-256:

`53dd49b8b9ab98de0dd240c6ef31862cd2d04298ed33b7a57562f81269a8f3aa`

It preserves the validated application/course payload while correcting stale release-document hashes, obsolete Android secret naming, historical report ambiguity, and third-party notice wording.

The independent public-release preflight run `33692316184` passed all credential-free release gates:

- exact first-party source/content audit: PASS
- locked npm dependency resolution: PASS
- npm audit: zero vulnerabilities reported
- locked Rust dependency resolution: PASS
- RustSec blocking vulnerability gate: PASS, zero known vulnerabilities
- complete `cargo-about` third-party license report: GENERATED/PASS
- Tauri iOS App Store Connect export CLI surface on macOS: PASS

RustSec also reports upstream informational `unsound`/`unmaintained` warnings in the current stable Tauri Linux GTK3 dependency stack. They are documented in `SECURITY_RELEASE_REVIEW.md`; no known RustSec vulnerability was found.

## Final release workflow — repository-side state

`.github/workflows/final-signed-release.yml` has been hardened and is now the canonical final release pipeline.

Its exact hardened workflow was independently YAML-validated before commit. The committed workflow then ran successfully on the release branch (run `33695025084`) and again from `main` (run `33695098420`) in push/preflight mode.

Those runs proved that the final workflow can:

1. retrieve the normalized production-source artifact;
2. verify its exact SHA-256 and canonical frontend/portable/course hashes;
3. rerun the first-party audit;
4. retrieve the independent security/license evidence;
5. require successful npm/RustSec gates and the generated license report.

On ordinary pushes, only this credential-free `pipeline_preflight` executes. Platform signing/build jobs deliberately run only from an explicit manual `workflow_dispatch`, preventing accidental credential-dependent release attempts.

The earlier private draft-release source archive remains useful as an owner archival copy, but the final CI pipeline no longer depends on it: testing showed the workflow token could not reliably retrieve that private draft asset. The final workflow instead consumes the proven normalized production-source Actions artifact above. Keep an owner-controlled offline/private archival copy of the normalized source because Actions artifacts are retention-limited.

## Platform matrix

| Platform | Existing validated state | Final manual-release gate |
| --- | --- | --- |
| Windows x64 | NSIS + MSI build PASS; GUI smoke PASS | Publisher Authenticode certificate; app executable + NSIS + MSI must all verify `Valid`; signed app smoke |
| Linux x64 | AppImage + DEB build PASS; GUI smoke PASS | Rebuild from normalized source and repeat AppImage runtime smoke |
| macOS Apple Silicon | DMG build PASS | Developer ID signing, notarization/stapling, Gatekeeper/codesign verification, native Apple-Silicon launch smoke |
| macOS Intel | DMG build PASS | Developer ID signing, notarization/stapling, Gatekeeper/codesign verification, native Intel launch smoke |
| Android | APK/AAB build PASS | Permanent publisher signing, API 36 metadata, 16 KB ZIP/ELF checks, signature verification, Android 15 16 KB signed-APK runtime smoke |
| iOS | No-sign native compile PASS | Apple Distribution certificate/profile import, signed App Store Connect IPA, codesign/profile verification |

The iOS IPA produced by the final workflow is an **App Store Connect submission artifact**, not a universal direct-download iOS installer for arbitrary website/itch.io sideloading.

## Required publisher credentials

### Android

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEY_ALIAS`
- `ANDROID_STORE_PASSWORD`
- `ANDROID_KEY_PASSWORD`

Use one permanent owner-controlled release identity for v1.0.0 and future updates.

### Windows

- `WINDOWS_CERTIFICATE_BASE64`
- `WINDOWS_CERTIFICATE_PASSWORD`

Optional repository variable:

- `WINDOWS_TIMESTAMP_URL` — falls back to `http://timestamp.digicert.com` if absent.

### macOS

- `MACOS_CERTIFICATE_BASE64`
- `MACOS_CERTIFICATE_PASSWORD`
- `MACOS_KEYCHAIN_PASSWORD`
- `APPLE_API_ISSUER`
- `APPLE_API_KEY`
- `APPLE_API_PRIVATE_KEY_BASE64`

### iOS

- `IOS_CERTIFICATE`
- `IOS_CERTIFICATE_PASSWORD`
- `IOS_MOBILE_PROVISION`
- `APPLE_DEVELOPMENT_TEAM`

Do not send these secret values through chat or commit them to the repository.

## Final public package policy

When every credentialed platform job succeeds, CI assembles:

`GDScript-Lab-v1.0.0-ALL-PLATFORMS-FINAL.zip`

The final public package is designed to contain:

- signed/verified Windows distributables;
- Linux AppImage + DEB;
- signed/notarized macOS DMGs for Intel and Apple Silicon;
- permanent publisher-signed Android APK + AAB;
- signed App Store Connect iOS IPA;
- validated self-contained portable HTML edition;
- public legal/support/accessibility documentation;
- third-party notices and complete generated license report;
- security/preflight and platform verification evidence;
- final SHA-256 manifest.

The proprietary build-source archive is **not included** in the public package. No private signing key, keystore, PFX/P12 private-key file, password, provisioning secret, or Apple API private key is included.

## What remains before public launch

Repository/application engineering work is complete to the extent possible without publisher identities. The remaining release blockers are owner/account-controlled:

1. Configure the permanent Android publisher secrets.
2. Configure the trusted Windows Authenticode certificate secrets.
3. Configure the macOS Developer ID/notarization secrets.
4. Configure the iOS Apple Distribution/provisioning secrets and ensure the App ID/profile match `com.jbhprods.gdscriptlab`.
5. Manually dispatch `.github/workflows/final-signed-release.yml`.
6. Require **every** platform job and final packaging job to pass.
7. Independently inspect the resulting signatures, notarization/provisioning evidence, runtime-smoke evidence, final ZIP and SHA-256 manifest.
8. Submit the iOS artifact through the appropriate Apple distribution channel and, ideally, validate the final build on physical target devices before broad launch.
9. Publish the generated draft `v1.0.0` release/store files only after those checks.

Until steps 1–9 are completed, the existing all-platform ZIP must continue to be described as an RC rather than a universally signed final production release.
