#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path

EXPECTED_FRONTEND='628151d40b067f8ab55da80030862720d319d07f69d62d5b532bfd0fdc311336'
EXPECTED_PORTABLE='e9961e8ed86526cff1a51725dd013c4370a159754642f3c6628779202095108d'
EXPECTED_COURSE='c0a663fb0cf5cf8876e3279e70d5783d245a615cbf6238cf82a1ad67e1408abe'
NDK='29.0.14206865'

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f'Cannot finalize {label}: expected source text not found')
    return text.replace(old,new,1)

def main() -> None:
    if len(sys.argv)!=2:
        raise SystemExit('usage: finalize-v1-source.py PROJECT_DIR')
    root=Path(sys.argv[1]).resolve()
    if not root.is_dir(): raise SystemExit(f'Project directory not found: {root}')

    frontend=root/'src/index.html'
    portable=root/'portable/GDScript_Lab_Godot47_v1.0.0.html'
    if sha(frontend)!=EXPECTED_FRONTEND: raise SystemExit('Frontend hash mismatch before finalization')
    if sha(portable)!=EXPECTED_PORTABLE: raise SystemExit('Portable hash mismatch before finalization')
    html=frontend.read_text('utf-8')
    m=re.search(r'window\.COURSE_DATA\s*=\s*',html)
    if not m: raise SystemExit('COURSE_DATA block not found')
    s=m.end(); depth=0; ins=False; esc=False; end=None
    for i,ch in enumerate(html[s:],s):
        if ins:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': ins=False
        else:
            if ch=='"': ins=True
            elif ch=='{': depth+=1
            elif ch=='}':
                depth-=1
                if depth==0:
                    end=i+1; break
    if end is None: raise SystemExit('COURSE_DATA object end not found')
    raw=html[s:end]
    if hashlib.sha256(raw.encode()).hexdigest()!=EXPECTED_COURSE:
        raise SystemExit('Course data hash mismatch before finalization')

    conf_p=root/'src-tauri/tauri.conf.json'
    conf=json.loads(conf_p.read_text('utf-8'))
    if conf.get('identifier')!='com.jbhprods.gdscriptlab' or conf.get('version')!='1.0.0':
        raise SystemExit('Unexpected app identity/version')
    conf['bundle']['android']['versionCode']=1000000
    conf['bundle']['android']['autoIncrementVersionCode']=False
    conf['bundle']['iOS']['minimumSystemVersion']='15.0'
    conf['bundle']['iOS']['bundleVersion']='1'
    conf_p.write_text(json.dumps(conf,indent=2,ensure_ascii=False)+'\n','utf-8')

    cargo_dir=root/'.cargo'; cargo_dir.mkdir(exist_ok=True)
    (cargo_dir/'config.toml').write_text('''# Android-only ELF page-alignment policy for GDScript Lab v1.0.0.\n# NDK r28+ aligns 16 KiB by default; explicit linker flags make the release requirement deterministic.\n[target.'cfg(target_os = "android")']\nrustflags = [\n  "-C", "link-arg=-Wl,-z,max-page-size=16384",\n  "-C", "link-arg=-Wl,-z,common-page-size=16384",\n]\n''','utf-8')

    android_p=root/'.github/workflows/android-build.yml'
    t=android_p.read_text('utf-8').replace('Android NDK 27.2','Android NDK r29').replace('27.2.12479018',NDK)
    android_p.write_text(t,'utf-8')

    ios_p=root/'.github/workflows/ios-build.yml'
    t=ios_p.read_text('utf-8')
    if 'Require Xcode 26+ / iOS 26 SDK+' not in t:
        needle='      - uses: actions/checkout@v7\n'
        gate='''      - uses: actions/checkout@v7\n      - name: Require Xcode 26+ / iOS 26 SDK+\n        shell: bash\n        run: |\n          set -euo pipefail\n          xcodebuild -version\n          XCODE_MAJOR="$(xcodebuild -version | awk '/Xcode/{split($2,v,"."); print v[1]; exit}')"\n          test -n "$XCODE_MAJOR" && test "$XCODE_MAJOR" -ge 26\n          xcrun --sdk iphoneos --show-sdk-version | tee /tmp/gdlab-ios-sdk-version.txt\n          SDK_MAJOR="$(cut -d. -f1 </tmp/gdlab-ios-sdk-version.txt)"\n          test "$SDK_MAJOR" -ge 26\n'''
        if needle not in t: raise SystemExit('Cannot insert Xcode gate')
        t=t.replace(needle,gate,1)
    ios_p.write_text(t,'utf-8')

    audit_p=root/'scripts/audit.py'
    t=audit_p.read_text('utf-8')
    t=replace_once(t,"assert conf['bundle']['iOS']['minimumSystemVersion']=='14.0'", "assert conf['bundle']['iOS']['minimumSystemVersion']=='15.0'\nassert conf['bundle']['iOS']['bundleVersion']=='1'\nassert conf['bundle']['android']['versionCode']==1000000",'audit mobile versions')
    if "android_linker=Path('.cargo/config.toml')" not in t:
        needle="assert conf['app']['security']['csp'] is None\n"
        extra="""assert conf['app']['security']['csp'] is None\n# The authoritative CSP is the document-level policy in src/index.html; keeping\n# Tauri's optional CSP transform disabled avoids changing already validated desktop/Android payload semantics.\nassert \"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src ipc: http://ipc.localhost; object-src 'none'; base-uri 'none'; form-action 'none'\" in t\nandroid_linker=Path('.cargo/config.toml').read_text('utf-8')\nassert 'max-page-size=16384' in android_linker and 'common-page-size=16384' in android_linker\n"""
        if needle not in t: raise SystemExit('Cannot insert linker/CSP audit')
        t=t.replace(needle,extra,1)
    t=t.replace("assert \"ndk;27.2.12479018\" in android_wf",f"assert \"ndk;{NDK}\" in android_wf")
    audit_p.write_text(t,'utf-8')

    readme_p=root/'README_BUILD.md'
    t=readme_p.read_text('utf-8').replace('- iOS minimum: **14.0**','- iOS minimum: **15.0**')
    if 'Android `versionCode`' not in t:
        t=t.replace('- Android minimum: **API 24 / Android 7.0**\n','- Android minimum: **API 24 / Android 7.0**\n- Android `versionCode`: **1000000** (future Google Play uploads must increase it)\n',1)
    if 'iOS bundle/build number' not in t:
        t=t.replace('- iOS minimum: **15.0**\n','- iOS minimum: **15.0**\n- iOS bundle/build number: **1** (future App Store uploads must increase it)\n',1)
    readme_p.write_text(t,'utf-8')

    report_p=root/'BUILD_ATTEMPT_REPORT.md'
    report_p.write_text(report_p.read_text('utf-8').replace('NDK `27.2.12479018`',f'NDK `{NDK}`'),'utf-8')

    manifest_p=root/'BUILD_MANIFEST.json'
    manifest=json.loads(manifest_p.read_text('utf-8'))
    manifest['manifest_generated_at']='2026-09-03'
    manifest.setdefault('toolchains',{})['android_ndk']=NDK
    manifest.setdefault('platform_minimums',{})['ios']='15.0'
    manifest['mobile_build_identity']={'android_version_code':1000000,'ios_bundle_version':'1'}
    manifest['android_16kb_linker_policy']='.cargo/config.toml'
    manifest['release_finalization']={'xcode_min_major':26,'ios_sdk_min_major':26,'android_target_api':36,'android_ndk':NDK,'course_payload_changed':False}
    manifest_p.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n','utf-8')

    final_report=root/'PRODUCTION_FINALIZATION_REPORT.md'
    if not final_report.exists():
        final_report.write_text(f'''# GDScript Lab v1.0.0 — Production Finalization Record\n\nFinalization date: 2026-09-03\n\nThe learner/course payload is frozen. Frontend SHA-256 `{EXPECTED_FRONTEND}`, portable SHA-256 `{EXPECTED_PORTABLE}`, and COURSE_DATA SHA-256 `{EXPECTED_COURSE}` are unchanged. Release corrections set Android API-36/NDK-r29 policy, explicit Android versionCode 1000000, explicit 16 KiB ELF linker alignment, iOS minimum 15.0, iOS bundle/build number 1, and an Xcode-26/iOS-26-SDK CI gate. No private signing credentials are included.\n''','utf-8')

    if sha(frontend)!=EXPECTED_FRONTEND or sha(portable)!=EXPECTED_PORTABLE:
        raise SystemExit('Learner payload changed during finalization')
    print('PASS: production source finalization complete with frozen learner/course payload')

if __name__=='__main__': main()
