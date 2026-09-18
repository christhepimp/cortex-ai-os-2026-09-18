# Rooted Android emulator — getting inside Linux

## Why an emulator, not a phone

- Snapshots: if a userspace takeover bricks init, roll back.
- `adb root` works on `google_apis` / AOSP images without Magisk.
- Goldfish/ranchu kernels are public (AOSP `kernel/goldfish`, `kernel/common`).
- You can attach gdb to QEMU (`-qemu -s -S`) for kernel research.

## Path A — Android Studio AVD (recommended)

1. Install Android Studio / cmdline-tools + an emulator system image:
   - **Use `Google APIs` or AOSP**, not `Google Play`.
   - Play images lock `adbd` unprivileged; you then need Magisk + [rootAVD](https://gitlab.com/newbit/rootAVD).
2. Create AVD, start it:
   ```bash
   emulator -list-avds
   emulator -avd YOUR_AVD -writable-system
   adb wait-for-device
   adb root
   adb shell uname -a
   adb shell id
   ```
3. You are now root on Linux. Typical kernel string:
   `Linux localhost 5.x.x-android14-... #1 SMP PREEMPT ... x86_64`
4. Explore:
   ```bash
   adb shell cat /proc/version
   adb shell ls /sys
   adb shell ps -A | head
   adb shell cat /init.rc | head
   ```

### Play Store image + Magisk (if you need Play)

- rootAVD patches the ramdisk of the AVD and installs Magisk.
- After reboot: Magisk app → grant shell `su`.
- Then `adb shell su -c id`.

## Path B — Genymotion

- Personal edition, pick a Google APIs / custom image.
- Enable root in device settings or `adb shell su`.
- Faster UI; slightly less "vanilla kernel" than AOSP emulator.

## Path C — Research root of Play images (Android_Emuroot)

- https://github.com/airbus-seclab/android_emuroot
- Starts emulator with QEMU GDB stub, patches task credentials in kernel memory.
- Version-locked to specific API / kernel builds. Lab toy, not daily driver.

## Path D — Custom Goldfish kernel

- https://github.com/fries/android-emulator-root
- AOSP: `git clone https://android.googlesource.com/kernel/goldfish`
- Point the emulator at your `bzImage` / Image.gz with `-kernel` / `kernel-ranchu`.
- This is the *only* honest way to "change Linux" under the emulator.

## What you will *not* do from an APK

Replacing Linux from inside an unprivileged Android app is not a thing. You need root *or* a custom kernel *or* a second VM (QEMU-in-Android / AVF). Cortex assumes Path A root.
