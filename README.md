# Cortex AI-OS Lab (2026-09-18)

**Goal:** Start from a *rooted Android emulator* (real Linux kernel + Android userspace), get a root shell *inside* that Linux, then slowly put an **AI in charge of the OS** so the operating system *behaves as an AI* — without pretending we can delete Linux in one weekend.

Repo: https://github.com/christhepimp/cortex-ai-os-2026-09-18

## Honest architecture (what actually works)

You cannot rip the Linux kernel out of Android Studio / Genymotion / QEMU and drop in a homemade "AI kernel" while the emulator still boots. Those emulators *are* Linux (Goldfish / ranchu kernels). Hardware, processes, memory, filesystems, and drivers live there.

What *is* possible, and what this repo builds:

1. Boot a **rooted** Android virtual device (AVD).
2. `adb root` / Magisk / `su` → full Linux userspace as root.
3. Run **Cortex** — a userspace AI control plane — as PID-adjacent supervisor.
4. Gradually *replace decisions* (scheduling hints, process policy, package installs, network allow/deny, init scripts) with the AI.
5. Keep Linux as the body. Make the AI the brain.

That *is* "the OS itself is an AI" in the only sense that ships.

```
[ you / natural language ]
          |
    Cortex control plane   <-- this repo (Python)
          |
   Android userspace (init, zygote, apps)
          |
   Linux kernel (Goldfish/ranchu)  <-- stays
          |
   QEMU / Android Emulator hypervisor
```

## Rooted Android emulators that fit this lab

| Path | Root? | Linux access | Notes |
|---|---|---|---|
| **Android Studio Emulator (AVD) + Google APIs / AOSP image** | Yes (`adb root` on `-google_apis` or AOSP; Play Store images need Magisk/rootAVD) | Full `/` as root, `uname -a` is Linux | Best lab. Kernel is Goldfish/ranchu. Custom kernels possible. |
| **Genymotion Desktop** | Yes (built-in root toggle on many images) | `adb shell` + su | Fast. VirtualBox/QEMU backend. |
| **Android_Emuroot** (Airbus) | On-the-fly root of Play Store AVDs via QEMU GDB stub | Kernel task cred patch | Research-only; version-specific. |
| **fries/android-emulator-root** | `su` + custom emulator kernels | Goldfish kernel builds | Older but documents the kernel path. |
| Gaming emulators (BlueStacks, LDPlayer) | Sometimes a "root" toggle | Opaque, not a clean Linux lab | Avoid for kernel work. |

Recommended start: **Android Studio AVD, system image `google_apis` x86_64 or arm64, API 33+**, then `adb root && adb shell`.

See [docs/EMULATOR.md](docs/EMULATOR.md).

## How we "replace Linux" without bricking the VM

Phased takeover (see [docs/PHASES.md](docs/PHASES.md)):

| Phase | What changes | What stays |
|---|---|---|
| 0 | Lab + root shell + telemetry | Everything |
| 1 | Cortex observes (ps, /proc, logcat, netstat) | init, zygote |
| 2 | Cortex *advises* (allow/deny process, cap network) | kernel |
| 3 | Cortex owns userspace policy (init overlays, Magisk modules) | kernel + drivers |
| 4 | Custom userspace PID 1 *next to* Android (chroot / namespace) | host kernel |
| 5 | Research: custom kernel modules / goldfish kernel forks | hypervisor |

Phase 5 is optional and years of work. Phases 0–3 are this repo.

## Quick start (host with Android SDK)

```bash
# 1. Create / start a google_apis AVD (not Play Store if you want adb root)
emulator -avd cortex_api34 -no-snapshot-load &

# 2. Root the adbd daemon
adb wait-for-device
adb root
adb remount   # if the image allows it

# 3. Push and run Cortex
adb push cortex /data/local/tmp/cortex
adb shell chmod +x /data/local/tmp/cortex/cortex.py
adb shell "cd /data/local/tmp/cortex && python3 cortex.py --once"
```

No Android SDK on this machine? Run the **host simulation** (same control loop, fake /proc):

```bash
python3 cortex/cortex.py --simulate --once
```

## Repo layout

```
cortex/           AI control plane
docs/             emulator + phase plan
scripts/          adb helpers
```

## License

MIT. Research lab, not a shipping OS.
