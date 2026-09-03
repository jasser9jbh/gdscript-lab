#!/usr/bin/env bash
set -euo pipefail

APK="${1:?Usage: android-16k-runtime-check.sh APK OUT_DIR LABEL}"
OUT="${2:?Usage: android-16k-runtime-check.sh APK OUT_DIR LABEL}"
LABEL="${3:-Android APK}"
PACKAGE="com.jbhprods.gdscriptlab"
ACTIVITY="${PACKAGE}/.MainActivity"

mkdir -p "$OUT"

# Record the emulator's actual kernel page size before touching the app.
adb shell getconf PAGE_SIZE | tr -d '\r' | tee "$OUT/PAGE_SIZE.txt"
if ! grep -qx '16384' "$OUT/PAGE_SIZE.txt"; then
  printf 'FAIL: emulator PAGE_SIZE is not 16384.\n' | tee "$OUT/RESULT.txt"
  exit 1
fi

# Preserve install and launch output even when a later assertion fails.
if ! adb install -r "$APK" 2>&1 | tee "$OUT/ADB_INSTALL.txt"; then
  printf 'FAIL: adb install failed for %s.\n' "$LABEL" | tee "$OUT/RESULT.txt"
  exit 1
fi

adb logcat -c || true
adb shell am force-stop "$PACKAGE" || true
if ! adb shell am start -W -n "$ACTIVITY" 2>&1 | tee "$OUT/AM_START.txt"; then
  adb logcat -d -v threadtime > "$OUT/LOGCAT.txt" 2>&1 || true
  adb shell dumpsys activity activities > "$OUT/DUMPSYS_ACTIVITY.txt" 2>&1 || true
  printf 'FAIL: Activity Manager could not start %s.\n' "$LABEL" | tee "$OUT/RESULT.txt"
  exit 1
fi

sleep 12
PID="$(adb shell pidof "$PACKAGE" 2>/dev/null | tr -d '\r' || true)"
printf '%s\n' "$PID" | tee "$OUT/PIDOF.txt"
adb logcat -d -v threadtime > "$OUT/LOGCAT.txt" 2>&1 || true
adb shell dumpsys activity activities > "$OUT/DUMPSYS_ACTIVITY.txt" 2>&1 || true
adb shell dumpsys package "$PACKAGE" > "$OUT/DUMPSYS_PACKAGE.txt" 2>&1 || true

grep -Ei 'FATAL EXCEPTION|AndroidRuntime|linker|dlopen|SIG(SEGV|ABRT|BUS)|Process: com\.jbhprods\.gdscriptlab|com\.jbhprods\.gdscriptlab' "$OUT/LOGCAT.txt" > "$OUT/RELEVANT_LOGCAT.txt" || true

if [[ -z "$PID" ]]; then
  printf 'FAIL: %s did not remain alive for 12 seconds on the Android 15 16-KB emulator.\n' "$LABEL" | tee "$OUT/RESULT.txt"
  exit 1
fi

printf 'PASS: %s stayed alive for 12 seconds on Android 15 with PAGE_SIZE=16384 (PID %s).\n' "$LABEL" "$PID" | tee "$OUT/RESULT.txt"
