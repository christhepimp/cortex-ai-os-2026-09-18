#!/usr/bin/env bash
# Push Cortex onto a running rooted AVD and run one cycle.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
adb wait-for-device
adb root || true
adb shell mkdir -p /data/local/tmp/cortex
adb push "$ROOT/cortex/cortex.py" /data/local/tmp/cortex/cortex.py
adb shell chmod 755 /data/local/tmp/cortex/cortex.py
echo "--- device identity ---"
adb shell uname -a || true
adb shell id || true
echo "--- cortex --once ---"
adb shell "python3 /data/local/tmp/cortex/cortex.py --once" || \
  adb shell "python /data/local/tmp/cortex/cortex.py --once" || \
  echo "No python on device. Run: python3 cortex/cortex.py --simulate --once"
