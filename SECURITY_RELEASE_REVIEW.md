# GDScript Lab v1.0.0 — Dependency Security Review

Review date: 2026-09-02

This file records the dependency-security state of the v1.0.0 production candidate. It is release engineering evidence, not a claim that any software dependency graph can be risk-free forever.

## Gates completed

The public-release preflight resolves the exact locked npm and Rust dependency graphs used by the corrected v1.0.0 source and performs explicit advisory scans.

- `npm audit --audit-level=moderate`: **PASS — 0 vulnerabilities at all severities**
- `cargo audit`: **PASS — 0 RustSec vulnerabilities**
- full `cargo-about` third-party license report: **generated successfully**
- first-party source audit: **PASS**
- Tauri iOS App Store Connect export CLI probe on macOS: **PASS**

Evidence is produced by `.github/workflows/public-release-preflight.yml`.

## Informational RustSec warnings

`cargo audit` also reports informational warnings that do not make its vulnerability gate fail:

- 16 unmaintained-package warnings
- 1 unsoundness warning: `RUSTSEC-2024-0429` for `glib 0.18.5`

The unmaintained GTK3-family crates enter the graph through Tauri's Linux GTK3/WebKitGTK backend. The `unic-*` warnings enter through `tauri-utils -> urlpattern`. They are not first-party GDScript Lab dependencies.

### RUSTSEC-2024-0429 risk decision

The advisory affects iterator methods of `glib::VariantStrIter` in `glib >=0.15,<0.20`. The GDScript Lab Rust application crate does not directly depend on `glib`, `gtk`, or `gdk`, and its first-party Rust source does not call `VariantStrIter`. The dependency path is transitive, for example:

`gdscript-lab -> tauri 2.11.5 -> gtk 0.18.2 -> glib 0.18.5`

The patched GLib Rust binding generation begins at `glib 0.20`, but Tauri 2.11.5's current Linux backend still uses GTK 0.18 / GTK3. Forcing `glib 0.20+` into that graph would mix incompatible gtk-rs generations and is not an application-level safe fix. Upstream Tauri/tao/wry GTK4 migration remains the appropriate resolution path.

**v1.0.0 decision:** temporarily accept this *Linux-only transitive informational risk* rather than ship an unreviewed framework fork or unfinished GTK4 migration. The Linux AppImage/DEB have already passed native build and GUI-smoke validation. This exception does not apply to Windows, macOS, Android or iOS dependency paths.

## Compensating controls

- Cargo and npm dependency versions are lockfile-pinned.
- Public-release CI fails on actual npm/RustSec vulnerabilities.
- The advisory inventory is retained as release evidence.
- The first-party app exposes no direct `glib::VariantStrIter` API surface.
- Linux release artifacts receive native GUI smoke testing.
- Re-check Tauri/GTK4 migration and `RUSTSEC-2024-0429` before the next product release and no later than 2026-10-15.

## Publication implication

This review does **not** make the current unsigned release candidate a final public release. Publisher signing/notarization/provisioning gates still have to pass. It records that there is no known npm or RustSec vulnerability blocking v1.0.0 at the time of this review, while preserving the upstream informational exception transparently.
