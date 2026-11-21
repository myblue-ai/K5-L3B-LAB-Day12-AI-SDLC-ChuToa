"""Tạo bằng chứng cho một phase: chạy test, kiểm tất định, chạy chuỗi sáng -> kho -> tối, kiểm danh sách nhóm.

    python3 tools/proof.py 1        # ghi vào docs/proof/phase-1/

Chỉ dùng thư viện chuẩn. Mỗi file bằng chứng ghi lệnh đã chạy, mã thoát và đầu ra thật (không sửa tay).
"""

import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "tests", "fixtures")


def headless():
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return shlex.split(json.load(f)["headless_cmd"])


def sh(cmd, env=None):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _short(c):
    """Đường dẫn trong repo -> tương đối; file tạm -> $TMP/<tên> (không lộ thư mục máy)."""
    if not os.path.isabs(c):
        return c
    try:
        rel = os.path.relpath(c, ROOT)
    except ValueError:
        rel = ".."
    return ("$TMP/" + os.path.basename(c)) if rel.startswith("..") else rel.replace(os.sep, "/")


def show(cmd):
    return " ".join(shlex.quote(_short(c)) for c in cmd)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(phase):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    out = os.path.join(ROOT, "docs", "proof", f"phase-{phase}")
    os.makedirs(out, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(["tests", "."]))
    summary = []

    # 1. toàn bộ test
    cmd = [*headless()[:1], "-m", "unittest", "discover", "-s", "tests", "-v"]
    code, text = sh(cmd, env)
    with open(os.path.join(out, "tests.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {stamp}\n$ PYTHONPATH=tests{os.pathsep}. {show(cmd)}\n# exit {code}\n\n{text}")
    last = [ln for ln in text.splitlines() if ln.startswith(("Ran ", "OK", "FAILED"))]
    summary.append(f"tests: exit {code} · {' · '.join(last)}")

    with tempfile.TemporaryDirectory() as tmp:
        # 2. tất định: cùng seed -> cùng byte (gather có input, quan có khách ngẫu nhiên)
        lines = []
        for mode, extra in (("gather", ["--inputs", os.path.join(FIX, "morning.inputs.json")]),
                            ("quan", ["--scenario", os.path.join(FIX, "evening.stock.json")])):
            hashes = []
            for i in (1, 2):
                p = os.path.join(tmp, f"{mode}{i}.jsonl")
                cmd = [*headless(), "--mode", mode, "--seed", "7", "--ticks", "3000", *extra, "--out", p]
                code, text = sh(cmd)
                hashes.append(sha(p) if code == 0 else f"exit {code}: {text.strip()}")
                lines.append(f"$ {show(cmd)}\n  exit {code} sha256 {hashes[-1]}")
            same = hashes[0] == hashes[1]
            lines.append(f"=> {mode}: hai lần chạy {'GIỐNG' if same else 'KHÁC'} từng byte\n")
            summary.append(f"determinism {mode}: {'same bytes' if same else 'DIFFERENT'}")
        with open(os.path.join(out, "determinism.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"# {stamp}\n" + "\n".join(lines))

        # 3. chuỗi sáng -> kho -> tối
        inv = os.path.join(tmp, "kho.json")
        g = os.path.join(tmp, "g.jsonl")
        q = os.path.join(tmp, "q.jsonl")
        c1 = [*headless(), "--mode", "gather", "--seed", "1", "--ticks", "10800",
              "--inputs", os.path.join(FIX, "morning.inputs.json"), "--inventory-out", inv, "--out", g]
        k1, t1 = sh(c1)
        kho = open(inv, encoding="utf-8").read() if os.path.exists(inv) else "(không có file kho)"
        c2 = [*headless(), "--mode", "quan", "--seed", "1", "--ticks", "1600", "--inventory", inv,
              "--inputs", os.path.join(FIX, "evening.inputs.json"), "--out", q]
        k2, t2 = sh(c2)

        def ev(path):
            if not os.path.exists(path):
                return []
            with open(path, encoding="utf-8") as f:
                return [json.loads(x) for x in f if x.strip()]

        gr, qr = ev(g), ev(q)
        body = [f"# {stamp}", f"$ {show(c1)}", f"  exit {k1} {t1.strip()}"]
        body += [f"  tick {r['tick']:>5} {r['name']} {json.dumps(r['data'], ensure_ascii=False)}" for r in gr if r["type"] == "event"]
        body += [f"  end: {json.dumps(gr[-1], ensure_ascii=False)}" if gr else "", f"kho.json = {kho.strip()}", ""]
        body += [f"$ {show(c2)}", f"  exit {k2} {t2.strip()}"]
        body += [f"  tick {r['tick']:>5} {r['name']} {json.dumps(r['data'], ensure_ascii=False)}" for r in qr if r["type"] == "event"]
        body += [f"  end: {json.dumps(qr[-1], ensure_ascii=False)}" if qr else ""]
        with open(os.path.join(out, "integration.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(body) + "\n")
        if os.path.exists(inv):
            with open(os.path.join(out, "kho.json"), "w", encoding="utf-8", newline="\n") as f:
                f.write(kho)
        summary.append(f"integration: gather exit {k1}, quan exit {k2}, kho {kho.strip()}, "
                       f"quan money {qr[-1]['money'] if qr else '?'}")

    # 4. danh sách nhóm
    code, text = sh([*headless()[:1], "tools/check_team.py"])
    with open(os.path.join(out, "check_team.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {stamp}\n$ python3 tools/check_team.py\n# exit {code}\n{text}")
    summary.append(f"check_team: exit {code} ({text.strip().splitlines()[-1] if text.strip() else ''})")

    with open(os.path.join(out, "SUMMARY.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Phase {phase} · {stamp}\n" + "\n".join(f"- {s}" for s in summary) + "\n")
    print("\n".join(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "1"))
