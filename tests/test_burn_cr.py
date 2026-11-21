"""Change request Phase 3 (ADR-0001): món chín để quá burn_s giây thì cháy.

game.contract.json giữ burn_s = null nên test bật burn_s bằng tuning sửa trong bộ nhớ (unit test starter Python).
"""

import copy
import unittest

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput
from chonoi.inputs import InputPlayer
from chonoi.runner import Session

DISH = "ca_loc_nuong_trui"


def tuning(burn_s):
    t = copy.deepcopy(load_contract()["tuning"])
    t["quan"]["burn_s"] = burn_s
    validate_tuning(t)
    return t


def play(t, scenario, frames, ticks):
    s, p, out = Session("quan", t, scenario, 1), InputPlayer(frames), []
    while s.tick < ticks and not s.done:
        out += s.step(p.advance(s.tick))
    return s, out


class Burn(unittest.TestCase):
    def test_contract_accepts_null_or_range(self):
        tuning(None)
        tuning(5)
        for bad in (0, 601, "5"):
            with self.assertRaises(BadInput):
                tuning(bad)

    def test_ready_dish_burns_after_burn_s(self):
        t = tuning(2)
        sc = {"random_customers": False, "stoves": [{"id": "B1", "state": "ready", "dish": DISH}]}
        s, ev = play(t, sc, [], 130)
        burnt = [e for e in ev if e["name"] == "dish_burnt"]
        self.assertEqual([(e["tick"], e["data"]) for e in burnt], [(120, {"stove_id": "B1", "dish_id": DISH})])
        self.assertEqual(s.sim.stoves[0]["state"], "idle")
        self.assertIsNone(s.sim.stoves[0]["dish"])

    def test_null_never_burns(self):
        sc = {"random_customers": False, "stoves": [{"id": "B1", "state": "ready", "dish": DISH}]}
        s, ev = play(tuning(None), sc, [], 600)
        self.assertEqual([e for e in ev if e["name"] == "dish_burnt"], [])
        self.assertEqual(s.sim.stoves[0]["state"], "ready")

    def test_recook_after_burn_uses_free_stock_only(self):
        """C1 đã nấu (reserved rỗng) nhưng món cháy; còn 1 cá lóc nhưng C2 đang giữ chỗ -> không được nấu lại cho C1."""
        t = tuning(1)
        base = {"random_customers": False, "player": {"pos": [2, 7]},
                "stoves": [{"id": "B1", "state": "ready", "dish": DISH}],
                "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "reserved": {}}]}
        frames = [{"tick": 70, "interact": True}]
        t2 = copy.deepcopy(t)  # tuning gốc chỉ có 1 bàn; C2 cần bàn thứ hai
        t2["quan"]["tables"].append({"id": "T2", "pos": [12, 2]})
        held = dict(base, stock={"ca_loc": 1},
                    customers=base["customers"] + [{"id": "C2", "table_id": "T2", "dish_id": DISH}])
        _, ev = play(t2, held, frames, 75)
        self.assertEqual([e["name"] for e in ev], ["dish_burnt"], "kho còn 1 nhưng đã thuộc C2 -> không nấu lại cho C1")
        free = dict(base, stock={"ca_loc": 1})
        _, ev = play(t, free, frames, 75)
        self.assertEqual([e["name"] for e in ev], ["dish_burnt", "cook_started"])
        self.assertEqual(ev[1]["data"]["customer_id"], "C1")


if __name__ == "__main__":
    unittest.main()
