"""Cửa sổ chơi chế độ quan (Phase 2, client/ui): đọc kho, chạy cùng lớp sim với headless, snapshot có trường UI cần.

Chỉ dành cho starter Python (giống test_live.py)."""

import unittest

from chonoi.contract import load_contract
from chonoi.inputs import LiveInputs
from chonoi.live import LiveGame


class LiveQuan(unittest.TestCase):
    def test_quan_window_reads_inventory_and_gets_customer(self):
        tuning = load_contract()["tuning"]
        game = LiveGame("quan", tuning, {}, 1, inventory={"ca_loc": 1})  # không start(): bước tay, không cần luồng
        first = tuning["quan"]["first_customer_tick"]
        for _ in range(first):
            game._tick_once()
        snap = game.session.snapshot()
        self.assertEqual(snap["stock"], {"ca_loc": 1})
        self.assertEqual(len(snap["customers"]), 1)
        c = snap["customers"][0]
        for key in ("table_id", "dish_id", "state", "patience_ticks_left"):  # trường index.html đọc
            self.assertIn(key, c)
        self.assertEqual([e["name"] for e in game.events], ["customer_arrived"])
        self.assertIsInstance(LiveInputs().advance().move, tuple)


if __name__ == "__main__":
    unittest.main()
