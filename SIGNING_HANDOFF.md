# GDScript Lab v1.0.0 — Production Signing Handoff

This document covers the publisher-controlled work that remains after application, native-build, security/license, and final-pipeline preflight validation. Current release state is tracked in `RELEASE_STATUS.md`. The canonical credential-gated automation is `.github/workflows/final-signed-release.yml`.

**Never paste private signing keys, certificate passwords, provisioning secrets, or Apple API private keys into chat, commits, issues, logs, or public artifacts. Add them directly to the repository's GitHub Actions secrets/settings.**

## 1. Android — permanent publisher identity

Package identity: `com.jbhprods.gdscriptlab`.

Use exactly one permanent publisher-owned release keystore for v1.0.0 and every future update distributed under this package identity. Do **not** generate a different release key on each CI run.

GitHub Actions secrets:

- `ANDROID_KEYSTORE_BASE64` — base64 encoding of the publisher-owned `.jks`/keystore
- `ANDROID_KEY_ALIAS` — release-key alias
- `ANDROID_STORE_PASSWORD` — keystore password
- `ANDROID_KEY_PASSWORD` — release-key password

Final CI acceptance gates:

1. API 36 package metadata and version `1.0.0`.
2. 16 KB APK ZIP alignment.
3. 16 KB ELF alignment for APK/AAB native libraries.
4. Permanent publisher signing of APK and AAB.
5. `apksigner verify` passes for the final APK.
6. `jarsigner -verify` passes for the final AAB.
7. The signed APK installs and remains alive on the Android 15 16 KB emulator.
8. The signer certificate SHA-256 is recorded as public release-identity evidence.
9. The private keystore/passwords are never uploaded as artifacts.

Keep an offline/private backup of the permanent Android keystore. Losing the signing identity can prevent seamless updates to direct-distribution users.

## 2. Windows — trusted Authenticode identity

Obtain a current trusted Windows **code-signing** certificate from a supported certificate provider. An ordinary TLS/SSL certificate is not sufficient.

GitHub Actions secrets:

- `WINDOWS_CERTIFICATE_BASE64` — base64 encoding of the publisher-owned `.pfx`
- `WINDOWS_CERTIFICATE_PASSWORD` — PFX export password

Optional repository variable:

- `WINDOWS_TIMESTAMP_URL` — timestamp service recommended by the certificate issuer. If omitted, CI falls back to `http://timestamp.digicert.com`.

Final CI acceptance gates:

1. Temporary import into the runner's CurrentUser certificate store only.
2. Tauri builds using an ephemeral signing configuration referencing the imported publisher certificate.
3. `Get-AuthenticodeSignature` returns `Valid` for the application executable itself.
4. `Get-AuthenticodeSignature` returns `Valid` for the final NSIS installer.
5. `Get-AuthenticodeSignature` returns `Valid` for the final MSI installer.
6. The signed application executable launches and remains alive for the smoke interval.
7. Final hashes are recomputed after signing.

Never commit the PFX or its password.

## 3. macOS — Developer ID + notarization

For direct downloads outside the Mac App Store, obtain/export a **Developer ID Application** certificate from the publisher's Apple Developer account and create App Store Connect API credentials for notarization.

GitHub Actions secrets:

- `MACOS_CERTIFICATE_BASE64` — base64 `.p12` containing the Developer ID Application certificate/private key
- `MACOS_CERTIFICATE_PASSWORD` — `.p12` export password
- `MACOS_KEYCHAIN_PASSWORD` — CI-only password used for the temporary runner keychain
- `APPLE_API_ISSUER` — App Store Connect API issuer ID
- `APPLE_API_KEY` — App Store Connect API key ID
- `APPLE_API_PRIVATE_KEY_BASE64` — base64 contents of the downloaded `AuthKey_<KEYID>.p8`

Final CI acceptance gates for **both** Apple Silicon and Intel:

1. Certificate imported only into an ephemeral runner keychain.
2. Developer ID Application identity is detected.
3. Tauri signs the `.app`/bundle and uses the configured Apple credentials for notarization.
4. `codesign --verify --deep --strict` passes.
5. Gatekeeper assessment passes.
6. `xcrun stapler validate` confirms a stapled notarization ticket.
7. The signed/notarized app launches on a native-architecture GitHub runner and remains alive for the smoke interval.
8. Final hashes are recomputed after notarization/signing.

The final pipeline uses a native Apple-Silicon runner for the arm64 build and a native Intel macOS runner for the x64 build.

## 4. iOS — Apple Distribution + provisioning

Apple Developer/App Store Connect must have an App ID that matches `com.jbhprods.gdscriptlab` and an App Store Connect distribution provisioning profile linked to an Apple Distribution certificate.

GitHub Actions secrets:

- `IOS_CERTIFICATE` — base64 exported Apple Distribution `.p12`
- `IOS_CERTIFICATE_PASSWORD` — `.p12` export password
- `IOS_MOBILE_PROVISION` — base64 App Store Connect `.mobileprovision`
- `APPLE_DEVELOPMENT_TEAM` — Apple Developer Team ID

The hardened workflow decodes/imports the distribution certificate into a temporary keychain, installs the provisioning profile in the runner's provisioning-profile directory, checks the profile TeamIdentifier and application identifier, and then runs the Tauri App Store Connect export.

Final CI acceptance gates:

1. Apple Distribution identity is present in the temporary keychain.
2. Provisioning profile TeamIdentifier matches `APPLE_DEVELOPMENT_TEAM`.
3. Provisioning application identifier matches `com.jbhprods.gdscriptlab`.
4. Signed build uses export method `app-store-connect`.
5. A `.ipa` is actually generated.
6. The extracted application passes `codesign --verify --deep --strict`.
7. An embedded provisioning profile exists and is revalidated from the resulting IPA.
8. Final hashes are recomputed.

The resulting IPA is an **App Store Connect submission artifact**. Do not market it as a universal direct-download/sideload installer for arbitrary iPhone/iPad users.

## 5. Verified production source

The canonical normalized build-source archive was produced by Actions run `33692246998`:

- artifact: `GDScript-Lab-v1.0.0-PRODUCTION-source`
- inner ZIP: `GDScript_Lab_v1.0.0_PRODUCTION_SOURCE.zip`
- SHA-256: `53dd49b8b9ab98de0dd240c6ef31862cd2d04298ed33b7a57562f81269a8f3aa`

The final workflow downloads that artifact by immutable run ID and verifies the ZIP plus the canonical frontend, portable, and course-data hashes before any platform release work.

A separate private draft-release source archive exists as an owner archival copy, but testing showed that the normal workflow token cannot reliably consume that draft asset. Therefore it is **not** the final workflow's active source path.

GitHub Actions artifacts are retention-limited. Keep the normalized production source in at least one additional owner-controlled private/offline archive for long-term reproducibility.

## 6. Security and third-party license evidence

Independent credential-free release preflight run `33692316184` generated and passed:

- first-party source audit;
- locked npm and Cargo dependency resolution;
- npm vulnerability report with zero reported vulnerabilities;
- RustSec blocking vulnerability gate with zero known vulnerabilities;
- complete generated `cargo-about` third-party license report;
- macOS Tauri iOS/App Store Connect CLI-surface validation.

The final pipeline requires these evidence files before platform jobs can proceed. `SECURITY_RELEASE_REVIEW.md` documents the accepted upstream informational GTK/GLib RustSec warnings separately from blocking known vulnerabilities.

## 7. Running the final workflow

The final workflow has two modes:

- **push/preflight mode:** credential-free `pipeline_preflight` only; platform release jobs are skipped deliberately;
- **manual `workflow_dispatch`:** after all publisher secrets are configured, the preflight passes first and then the full Linux/Windows/macOS/Android/iOS matrix executes.

Do not manually dispatch the final release merely to test whether secrets exist. Configure the complete publisher credential set first, then run it once as the actual final-release candidate.

## 8. Final package and release

Only when every required platform job succeeds does CI create:

`GDScript-Lab-v1.0.0-ALL-PLATFORMS-FINAL.zip`

and its SHA-256 file. It then creates or refreshes a **draft** GitHub Release tagged `v1.0.0` for final publisher inspection.

The final public ZIP is designed to include public distributables, validated portable HTML, legal/support/accessibility material, third-party notices/full generated license evidence, platform verification evidence, security-preflight evidence, and checksums.

The proprietary production-source ZIP is **not** included in the public package. The final public ZIP must never contain keystores, PFX/P12 private-key files, passwords, provisioning secrets, or Apple API private keys.

Before publishing the draft release, inspect the final ZIP, checksum file, Authenticode evidence, Android signer fingerprint/signature checks, macOS notarization/Gatekeeper evidence, iOS provisioning/codesign evidence, and runtime-smoke evidence. Physical-device validation is strongly recommended for the final mobile builds, especially iOS through Apple's intended distribution path.
