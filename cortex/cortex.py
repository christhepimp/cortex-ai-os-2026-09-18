#!/usr/bin/env python3
"""Cortex — userspace AI control plane for a rooted Android/Linux lab.

The model is the OS brain. Linux remains the body.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WATCH = {
    "surfaceflinger",
    "zygote",
    "zygote64",
    "system_server",
    "adbd",
    "logd",
    "vold",
    "netd",
}


def sh(cmd: list[str], timeout: int = 8) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (p.stdout or "") + (p.stderr or "")
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
        return f"err:{e}"


def read_text(path: str) -> str:
    try:
        return Path(path).read_text(errors="replace")
    except OSError as e:
        return f"err:{e}"


@dataclass
class Snapshot:
    ts: str
    host: str
    kernel: str
    uid_hint: str
    loadavg: str
    meminfo_head: str
    processes: list[str]
    notes: list[str]


def snapshot_real() -> Snapshot:
    notes: list[str] = []
    kernel = read_text("/proc/version").strip() or platform.platform()
    loadavg = read_text("/proc/loadavg").strip()
    mem = "\n".join(read_text("/proc/meminfo").splitlines()[:8])
    uid_hint = sh(["id"]).strip()
    ps_out = sh(["ps", "-A"])
    procs = [ln.strip() for ln in ps_out.splitlines() if ln.strip()][:80]
    if "uid=0" not in uid_hint and "root" not in uid_hint:
        notes.append("not root — policy apply is disabled even if --apply")
    return Snapshot(
        ts=datetime.now(timezone.utc).isoformat(),
        host=platform.node(),
        kernel=kernel[:240],
        uid_hint=uid_hint[:120],
        loadavg=loadavg[:80],
        meminfo_head=mem[:600],
        processes=procs,
        notes=notes,
    )


def snapshot_sim() -> Snapshot:
    return Snapshot(
        ts=datetime.now(timezone.utc).isoformat(),
        host="avd-sim",
        kernel="Linux localhost 5.15.0-android14-goldfish SMP x86_64",
        uid_hint="uid=0(root) gid=0(root)",
        loadavg="0.42 0.38 0.35 2/412 10821",
        meminfo_head="MemTotal:  2048000 kB\nMemFree:  900000 kB",
        processes=[
            "root     1     0  init",
            "root     318   1  zygote64",
            "system   512   318 system_server",
            "root     220   1  adbd",
            "u0_a42   2201  318 com.android.chrome",
        ],
        notes=["simulate=1 — no real /proc"],
    )


def decide(snap: Snapshot) -> list[dict[str, Any]]:
    """Tiny policy brain. Swap this function for a real model later."""
    actions: list[dict[str, Any]] = []
    names = " ".join(snap.processes).lower()
    for must in WATCH:
        present = must in names
        actions.append(
            {
                "type": "watch",
                "target": must,
                "present": present,
                "verb": "keep" if present else "note",
                "reason": "core Android/Linux process" if present else "not seen in ps snapshot",
            }
        )
    try:
        load1 = float(snap.loadavg.split()[0])
        if load1 > 4.0:
            actions.append(
                {
                    "type": "resource",
                    "verb": "warn",
                    "reason": f"loadavg[0]={load1} is high for a lab AVD",
                }
            )
    except (ValueError, IndexError):
        pass
    actions.append(
        {
            "type": "identity",
            "verb": "note",
            "reason": "Cortex is the decision layer. Linux remains PID 1 / kernel.",
        }
    )
    return actions


def apply_actions(actions: list[dict[str, Any]], do_apply: bool) -> list[dict[str, Any]]:
    results = []
    for a in actions:
        rec = dict(a)
        rec["applied"] = False
        if do_apply and a.get("verb") == "kill" and a.get("target"):
            rec["applied"] = True
            rec["result"] = sh(["killall", str(a["target"])])[:200]
        results.append(rec)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Cortex AI-OS control plane")
    ap.add_argument("--simulate", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--apply", action="store_true", help="actually run kill/apply (dangerous)")
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rounds = 1 if args.once else 10**9
    for i in range(rounds):
        snap = snapshot_sim() if args.simulate else snapshot_real()
        actions = decide(snap)
        results = apply_actions(actions, args.apply and not args.simulate)
        report = {"snapshot": asdict(snap), "actions": results}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"=== cortex {snap.ts} host={snap.host} ===")
            print(f"kernel: {snap.kernel}")
            print(f"id:     {snap.uid_hint}")
            print(f"load:   {snap.loadavg}")
            for n in snap.notes:
                print(f"note:   {n}")
            for a in results:
                print(f"  [{a.get('verb'):4}] {a.get('type')} {a.get('target','')} — {a.get('reason')}")
        if not args.once:
            time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
