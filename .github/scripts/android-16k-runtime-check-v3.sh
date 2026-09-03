#!/usr/bin/env bash
set -euo pipefail

APK="${1:?Usage: android-16k-runtime-check-v3.sh APK OUT_DIR LABEL}"
OUT="${2:?Usage: android-16k-runtime-check-v3.sh APK OUT_DIR LABEL}"
LABEL="${3:-Android APK}"
PACKAGE="com.jbhprods.gdscriptlab"
ACTIVITY="${PACKAGE}/.MainActivity"

mkdir -p "$OUT"

capture_system_state() {
  adb shell getprop ro.build.version.sdk 2>/dev/null | tr -d '\r' > "$OUT/ANDROID_SDK.txt" || true
  adb shell getprop ro.build.version.release 2>/dev/null | tr -d '\r' > "$OUT/ANDROID_RELEASE.txt" || true
  adb shell getprop ro.build.fingerprint 2>/dev/null | tr -d '\r' > "$OUT/BUILD_FINGERPRINT.txt" || true
  adb shell getconf PAGE_SIZE 2>/dev/null | tr -d '\r' > "$OUT/PAGE_SIZE.txt" || true
}

capture_runtime_evidence() {
  adb logcat -d -v threadtime > "$OUT/LOGCAT.txt" 2>&1 || true
  adb shell dumpsys activity activities > "$OUT/DUMPSYS_ACTIVITY.txt" 2>&1 || true
  adb shell dumpsys package "$PACKAGE" > "$OUT/DUMPSYS_PACKAGE.txt" 2>&1 || true
  adb shell cat /proc/meminfo > "$OUT/MEMINFO_AFTER.txt" 2>&1 || true
  grep -Ei 'FATAL EXCEPTION|AndroidRuntime|linker|dlopen|SIG(SEGV|ABRT|BUS)|system_server|lowmemorykiller|lmkd|Process: com\.jbhprods\.gdscriptlab|com\.jbhprods\.gdscriptlab' "$OUT/LOGCAT.txt" > "$OUT/RELEVANT_LOGCAT.txt" || true
}

capture_system_state
adb shell cat /proc/meminfo > "$OUT/MEMINFO_BEFORE.txt" 2>&1 || true
cat "$OUT/PAGE_SIZE.txt"
if ! grep -qx '16384' "$OUT/PAGE_SIZE.txt"; then
  printf 'FAIL_ENVIRONMENT_PAGE_SIZE: emulator PAGE_SIZE is not 16384.\n' | tee "$OUT/RESULT.txt"
  exit 2
fi

SYSTEM_SERVER_BEFORE="$(adb shell pidof system_server 2>/dev/null | tr -d '\r' || true)"
printf '%s\n' "$SYSTEM_SERVER_BEFORE" > "$OUT/SYSTEM_SERVER_PID_BEFORE.txt"
if [[ -z "$SYSTEM_SERVER_BEFORE" ]]; then
  printf 'FAIL_ENVIRONMENT_FRAMEWORK: system_server PID unavailable before app launch.\n' | tee "$OUT/RESULT.txt"
  exit 2
fi

if ! adb install -r "$APK" 2>&1 | tee "$OUT/ADB_INSTALL.txt"; then
  capture_runtime_evidence
  printf 'FAIL_APP_INSTALL: adb install failed for %s.\n' "$LABEL" | tee "$OUT/RESULT.txt"
  exit 1
fi

adb logcat -c || true
adb shell am force-stop "$PACKAGE" || true
if ! adb shell am start -W -n "$ACTIVITY" 2>&1 | tee "$OUT/AM_START.txt"; then
  capture_runtime_evidence
  printf 'FAIL_APP_LAUNCH: Activity Manager could not start %s.\n' "$LABEL" | tee "$OUT/RESULT.txt"
  exit 1
fi

sleep 15
APP_PID="$(adb shell pidof "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
SYSTEM_SERVER_AFTER="$(adb shell pidof system_server 2>/dev/null | tr -d '\r' || true)"
printf '%s\n' "$APP_PID" | tee "$OUT/PIDOF.txt"
printf '%s\n' "$SYSTEM_SERVER_AFTER" > "$OUT/SYSTEM_SERVER_PID_AFTER.txt"
capture_runtime_evidence

if [[ -z "$SYSTEM_SERVER_AFTER" || "$SYSTEM_SERVER_AFTER" != "$SYSTEM_SERVER_BEFORE" ]]; then
  printf 'FAIL_ENVIRONMENT_FRAMEWORK: Android system_server restarted during %s runtime test (before=%s after=%s).\n' "$LABEL" "$SYSTEM_SERVER_BEFORE" "${SYSTEM_SERVER_AFTER:-missing}" | tee "$OUT/RESULT.txt"
  exit 2
fi

if [[ -z "$APP_PID" ]]; then
  if grep -Eq "lowmemorykiller: Kill '${PACKAGE//./\\.}'|lowmemorykiller: Kill 'com\.jbhprods\.gdscriptlab'" "$OUT/LOGCAT.txt"; then
    grep -E "lowmemorykiller: Kill 'com\.jbhprods\.gdscriptlab'" "$OUT/LOGCAT.txt" > "$OUT/APP_LMK_KILL.txt" || true
    printf 'FAIL_ENVIRONMENT_MEMORY: Android lowmemorykiller killed %s while system_server stayed alive.\n' "$LABEL" | tee "$OUT/RESULT.txt"
    exit 2
  fi
  printf 'FAIL_APP_RUNTIME: %s did not remain alive for 15 seconds while system_server remained healthy and no LMKD kill was recorded.\n' "$LABEL" | tee "$OUT/RESULT.txt"
  exit 1
fi

SDK="$(cat "$OUT/ANDROID_SDK.txt" 2>/dev/null || true)"
REL="$(cat "$OUT/ANDROID_RELEASE.txt" 2>/dev/null || true)"
printf 'PASS: %s stayed alive for 15 seconds on Android %s (API %s), PAGE_SIZE=16384, app PID %s, stable system_server PID %s.\n' "$LABEL" "$REL" "$SDK" "$APP_PID" "$SYSTEM_SERVER_AFTER" | tee "$OUT/RESULT.txt"
