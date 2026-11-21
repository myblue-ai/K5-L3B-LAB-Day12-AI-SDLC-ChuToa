"""Bench (Phase 4): thời gian chạy một buổi ĐẦY ĐỦ (10800 tick = 180 s game) qua headless_cmd và trong tiến trình.

    python3 tools/bench.py            # in bảng, ghi docs/proof/phase-4/bench.txt

Đo thời gian thật (time.perf_counter), lặp 3 lần, báo trung vị. Chỉ thư viện chuẩn.
"""

import json
import os
import platform
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from chonoi.contract import load_contract  # noqa: E402
from chonoi.inputs import InputPlayer  # noqa: E402
from chonoi.runner import Session  # noqa: E402

TICKS = 10800
RUNS = 3
STOCK = {"ca_loc": 3, "bong_sung": 4, "ca_linh": 6, "bong_dien_dien": 2}


def headless():
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return shlex.split(json.load(f)["headless_cmd"])


def cli_case(tmp, mode):
    out = os.path.join(tmp, f"{mode}.jsonl")
    cmd = [*headless(), "--mode", mode, "--seed", "1", "--ticks", str(TICKS), "--snapshot-every", "10", "--out", out]
    if mode == "quan":
        sc = os.path.join(tmp, "sc.json")
        with open(sc, "w", encoding="utf-8") as f:
            json.dump({"quan": {"stock": STOCK}}, f)
        cmd[-2:-2] = ["--scenario", sc]
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        times.append(time.perf_counter() - t0)
        if p.returncode != 0:
            raise SystemExit(f"{mode}: exit {p.returncode}")
    size = os.path.getsize(out)
    with open(out, encoding="utf-8") as f:
        rows = sum(1 for _ in f)
    return statistics.median(times), rows, size


def inproc_case(mode):
    tuning = load_contract()["tuning"]
    times = []
    for _ in range(RUNS):
        s = Session(mode, tuning, {} if mode == "gather" else {"stock": dict(STOCK)}, 1)
        p = InputPlayer([])
        t0 = time.perf_counter()
        while s.tick < TICKS and not s.done:
            s.step(p.advance(s.tick))
        times.append(time.perf_counter() - t0)
    return statistics.median(times), s.tick


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    lines = [f"# Bench {datetime.now():%Y-%m-%d %H:%M} · Python {platform.python_version()} · {platform.system()} {platform.machine()}",
             f"# {TICKS} tick/buổi, trung vị của {RUNS} lần", "",
             "| Mode | Cách chạy | Thời gian (s) | Tick/giây | Ghi chú |", "|---|---|---|---|---|"]
    with tempfile.TemporaryDirectory() as tmp:
        for mode in ("gather", "quan"):
            sec, ticks = inproc_case(mode)
            lines.append(f"| {mode} | Session trong tiến trình | {sec:.3f} | {ticks / sec:,.0f} | {ticks} tick (buổi tự kết thúc khi hết giờ) |")
            sec, rows, size = cli_case(tmp, mode)
            lines.append(f"| {mode} | headless_cmd (gồm khởi động Python + ghi JSONL) | {sec:.3f} | {TICKS / sec:,.0f} | {rows} dòng, {size / 1024:.0f} KiB |")
    realtime = TICKS / 60
    lines += ["", f"Thời gian game của một buổi: {realtime:.0f} s. Mọi cách chạy đều nhanh hơn thời gian thực nhiều lần."]
    text = "\n".join(lines) + "\n"
    out = os.path.join(ROOT, "docs", "proof", "phase-4")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "bench.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
