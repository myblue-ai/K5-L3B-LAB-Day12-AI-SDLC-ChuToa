"""Tích hợp sáng -> kho -> tối (hộp đen): lặn bắt F1, hái N1, cập bến; quán đọc kho, nấu lẩu, phục vụ, thu tiền.

Input cố định ở tests/fixtures/{morning,evening}.inputs.json (cũng dùng cho docs/proof).
"""

import json
import os
import unittest

from helpers import ROOT, Workdir, events, read_jsonl, run_headless

FIX = os.path.join(ROOT, "tests", "fixtures")


class Chain(unittest.TestCase):
    def test_morning_inventory_feeds_evening_service(self):
        with Workdir() as w:
            inv = w.path("kho.json")
            code, err = run_headless("--mode", "gather", "--seed", "1", "--ticks", "10800",
                                     "--inputs", os.path.join(FIX, "morning.inputs.json"),
                                     "--inventory-out", inv, "--out", w.path("g.jsonl"))
            self.assertEqual(code, 0, err)
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {"bong_dien_dien": 1, "ca_linh": 3}})
            code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "1600", "--inventory", inv,
                                     "--inputs", os.path.join(FIX, "evening.inputs.json"), "--out", w.path("q.jsonl"))
            self.assertEqual(code, 0, err)
            rows = read_jsonl(w.path("q.jsonl"))
            names = [r["name"] for r in rows if r["type"] == "event"]
            self.assertEqual(names, ["customer_arrived", "cook_started", "dish_ready", "dish_picked", "served", "paid"])
            self.assertEqual(events(rows, "customer_arrived")[0]["data"]["dish_id"], "lau_ca_linh_dien_dien")
            self.assertEqual(rows[-1]["money"], 144)
            self.assertEqual(rows[-1]["score"], 444)


if __name__ == "__main__":
    unittest.main()
