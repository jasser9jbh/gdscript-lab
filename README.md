# GDScript Lab v1.0.0 — Tauri 2 Application

Production application source for **GDScript Lab**, using the frozen validated HTML as the authoritative educational payload.

- Product: GDScript Lab
- Publisher: Journey Beyond Horizons Productions (JBH PRODS)
- Bundle ID: `com.jbhprods.gdscriptlab`
- Version: `1.0.0`
- Frozen portable-source SHA-256: `743e2f2d038681473ee20989892f6a306f758b4d03ff4e9989826e082daab822`
- COURSE_DATA SHA-256: `569bc1d6e94096f495345274bc5083053e1d5fd9af4262d4549cb08cde6b5880`

## What is preserved

`portable/GDScript_Lab_Godot47_v1.0.0.html` is byte-for-byte identical to the frozen browser build. `src/index.html` keeps the complete embedded `COURSE_DATA` object byte-for-byte identical. All 183 learner-visible code/command blocks are unchanged.

## Native-shell adaptations

- Tauri 2 WebView shell for Windows, Linux, macOS, Android and iOS.
- User-initiated official Godot/JBH PRODS links open in the system browser through the Tauri opener plugin.
- Exports use a native Save dialog and native filesystem text write in packaged apps.
- The original browser Blob-download behavior remains only in the portable/non-Tauri edition.
- Local progress remains local WebView storage; no account, telemetry, analytics, ad network, updater, or automatic HTTP client is added.
- Safe-area handling is included for mobile notches/system bars.
- Portable HTML remains included for users who prefer the standalone browser edition.

## Native security model

The Tauri frontend permits Tauri's internal IPC endpoint in its CSP but does not grant arbitrary remote fetch access. Capabilities are limited to:

- Tauri core defaults needed by the application shell;
- Save dialog only;
- text-file writes to user-selected locations;
- system-browser opening only for:
  - `docs.godotengine.org`
  - `godotengine.org`
  - `jbhprods.com`

No shell plugin, HTTP plugin, updater, broad filesystem read permission or telemetry capability is included.

## Pinned release toolchain

- Node.js 22.16.0 in CI
- Rust 1.98.0
- Tauri crate 2.11.5
- Tauri CLI 2.11.4

## Validation

Run:

```bash
python scripts/check-build-env.py
python scripts/audit.py
```

The source package also contains the final validation evidence and the build-attempt report from the ChatGPT build environment.

See:

- `README_BUILD.md`
- `README_DISTRIBUTION.md`
- `RELEASE_CHECKLIST.md`
- `BUILD_ATTEMPT_REPORT.md`
- `THIRD_PARTY_NOTICES.md`
