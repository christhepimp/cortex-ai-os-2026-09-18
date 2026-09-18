# Replacement phases

## Phase 0 — Lab is real

- AVD boots.
- `adb root` works.
- `uname -a` shows Linux.
- Cortex can be pushed to `/data/local/tmp`.

## Phase 1 — Observe

Cortex reads:

- `/proc/stat`, `/proc/meminfo`, `/proc/loadavg`
- `ps -A`
- `logcat -d -t 50` (optional)
- own policy file

No writes except its log.

## Phase 2 — Advise

Cortex emits actions:

- `keep` / `warn` / `kill` candidate processes (allowlist)
- `note` about high load / low memory

In `--dry-run` (default) it only prints. `--apply` would call `kill` — only on the emulator, only on names you listed.

## Phase 3 — Own userspace policy

- Magisk module or overlay scripts that Cortex writes.
- `init.rc` snippets (dangerous; snapshot first).
- Network: iptables/nft via root (lab only).

## Phase 4 — Parallel userspace

- Namespace or chroot with a second PID 1 that Cortex supervises.
- Android keeps running; Cortex world is a sibling OS personality.

## Phase 5 — Kernel research (optional)

- Build goldfish/ranchu kernel.
- Load a tiny out-of-tree module that exports a `/dev/cortex` char device.
- Still Linux. Just Linux with an AI socket.

There is no Phase 6 that deletes Linux and still talks to the emulator GPU. Anyone selling that is selling a reboot loop.
