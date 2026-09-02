# GDScript Lab v1.0.0 — Production Signing Handoff

This document covers only the remaining publisher-credential work. Application functionality and unsigned/native validation are tracked in `RELEASE_STATUS.md`. The final credential-gated automation is `.github/workflows/final-signed-release.yml`.

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
4. `apksigner verify` passes for the final APK.
5. `jarsigner -verify` passes for the final AAB.
6. The signed APK installs and remains alive on the Android 15 16 KB emulator.
7. The signer certificate SHA-256 is recorded as public release identity evidence.
8. The private keystore/passwords are never uploaded as artifacts.

## 2. Windows — trusted Authenticode identity

Obtain a current trusted Windows **code-signing** certificate from a supported certificate provider. An ordinary TLS/SSL certificate is not sufficient.

GitHub Actions secrets:

- `WINDOWS_CERTIFICATE_BASE64` — base64 encoding of the publisher-owned `.pfx`
- `WINDOWS_CERTIFICATE_PASSWORD` — PFX export password

Optional repository variable:

- `WINDOWS_TIMESTAMP_URL` — timestamp service recommended by the certificate issuer. If omitted, CI falls back to `http://timestamp.digicert.com`.

Final CI acceptance gates:

1. Temporary import into the runner's CurrentUser certificate store only.
2. Tauri builds Authenticode-signed NSIS and MSI installers.
3. `Get-AuthenticodeSignature` returns `Valid` for both final installers.
4. The signed application executable launches and remains alive for the smoke interval.
5. Final hashes are recomputed after signing.

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
3. Tauri signs the `.app` and DMG and submits for notarization.
4. `codesign --verify --deep --strict` passes.
5. Gatekeeper assessment passes.
6. `xcrun stapler validate` confirms a stapled notarization ticket.
7. Final hashes are recomputed after notarization/signing.

## 4. iOS — Apple Distribution + provisioning

Apple Developer/App Store Connect must have an App ID that matches `com.jbhprods.gdscriptlab` and an App Store Connect distribution provisioning profile linked to an Apple Distribution certificate.

GitHub Actions secrets:

- `IOS_CERTIFICATE` — base64 exported Apple Distribution `.p12`
- `IOS_CERTIFICATE_PASSWORD` — `.p12` export password
- `IOS_MOBILE_PROVISION` — base64 App Store Connect `.mobileprovision`
- `APPLE_DEVELOPMENT_TEAM` — Apple Developer Team ID

Final CI acceptance gates:

1. Signed build uses export method `app-store-connect`.
2. A distributable `.ipa` is actually generated.
3. The extracted application passes `codesign --verify --deep --strict`.
4. An embedded provisioning profile exists.
5. The provisioning `application-identifier` ends in `com.jbhprods.gdscriptlab`.
6. Final hashes are recomputed.

## 5. Durable verified source

`.github/workflows/archive-verified-source.yml` verifies the corrected source ZIP at SHA-256:

`dc39f130eb650c08d5b8a3bea1b7a0ef392598fe98dd2af218734db24f2af4e4`

and stores it in a **draft** GitHub Release tagged `v1.0.0-corrected-source-archive`. The final signed workflow downloads from this durable archive rather than relying on a 90-day Actions artifact.

## 6. Final package and release

When all five platform jobs pass, CI creates:

`GDScript-Lab-v1.0.0-ALL-PLATFORMS-FINAL.zip`

and its SHA-256 file. It then creates or refreshes a **draft** GitHub Release tagged `v1.0.0`. The release remains draft so the publisher can inspect the exact final artifacts and evidence before making them public.

The final ZIP may contain public distributables, public verification evidence, source if intended, and checksums. It must never contain keystores, PFX/P12 private-key files, signing passwords, provisioning secrets, or Apple API private keys.
