# GDScript Lab v1.0.0 — Production Signing Handoff

This document covers only the remaining credential-dependent release work. Application functionality and unsigned/native build validation are tracked separately in `RELEASE_STATUS.md`.

## Android

Use one permanent publisher-owned Android signing identity for v1.0.0 and all future updates distributed under the same package identity `com.jbhprods.gdscriptlab`.

Required GitHub Actions secrets:

- `ANDROID_KEYSTORE_BASE64` — base64 encoding of the publisher-owned `.jks`/keystore file
- `ANDROID_KEY_ALIAS` — alias of the release key in that keystore
- `ANDROID_STORE_PASSWORD` — keystore password
- `ANDROID_KEY_PASSWORD` — key password

Production workflow:

`.github/workflows/final-android-production-v5-windows.yml`

Acceptance checks after the signed build:

1. APK signing verification passes with Android `apksigner verify`.
2. AAB signing verification/build step passes.
3. Package ID remains `com.jbhprods.gdscriptlab`.
4. Version remains `1.0.0` for this release.
5. SHA-256 checksums are regenerated for the signed APK and AAB.
6. The private keystore/passwords never appear in logs, release ZIPs, Actions artifacts, commits, or public documentation.
7. The same signing identity is retained securely for future upgrades.

## Windows

The validated NSIS and MSI installers function without Authenticode, but public distribution is better with a trusted code-signing certificate.

Recommended final checks:

1. Sign both `GDScript-Lab-v1.0.0-Setup.exe` and `GDScript-Lab-v1.0.0.msi` with the publisher's Authenticode certificate.
2. Apply a trusted timestamp during signing.
3. Verify the signature on a clean Windows system.
4. Re-run installer launch/smoke checks after signing.
5. Regenerate SHA-256 checksums.

Do not commit a certificate private key or password to the repository.

## macOS

For polished public distribution, sign the application/bundle with the publisher's Apple Developer ID identity and notarize the resulting DMGs.

For both Apple Silicon and Intel builds:

1. Sign all relevant application code with the correct Developer ID Application identity.
2. Build the DMG from the signed app.
3. Submit for Apple notarization.
4. Staple the notarization result where applicable.
5. Validate with macOS signing/Gatekeeper tools on a clean machine.
6. Regenerate SHA-256 checksums after the final signed/notarized packaging.

Apple private keys and account credentials must remain outside public repository history and public build artifacts.

## iOS

The current evidence is a successful no-sign native compile. A distributable IPA still needs a valid Apple signing/provisioning setup.

Final requirements:

1. Apple Developer team/account with an appropriate distribution certificate.
2. App identifier/provisioning configuration matching the intended bundle identity.
3. Signed archive/export producing a distributable IPA.
4. Installation/launch validation on a compatible real device or an appropriate distribution validation path.
5. Final checksum generation.

## Final release packaging rule

Only after the credential-dependent steps above are complete should the cross-platform bundle lose the `RC` designation.

The final release package should contain only public distributables, public verification/status text, source if intended, and checksums. It must not contain keystores, certificate private keys, signing passwords, Apple private credentials, or other secret material.
