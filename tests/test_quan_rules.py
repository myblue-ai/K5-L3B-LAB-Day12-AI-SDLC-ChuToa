"""Luật buổi tối (quan) của nhóm — lát 3 (khách, giữ chỗ, kiên nhẫn) và lát 4 (bếp, bưng, phục vụ, tiền, uy tín).

Test HỘP ĐEN qua headless_cmd. Giả định luật ghi ở docs/clarify.md (#7–#11).
"""

import json
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json

DISH = "ca_loc_nuong_trui"


def tuning():
    with open("game.contract.json", encoding="utf-8") as f:
        return json.load(f)["tuning"]


def run_q(w, scenario, inputs=None, ticks=10, every=1, seed=1, out="q.jsonl"):
    args = ["--mode", "quan", "--seed", str(seed), "--ticks", str(ticks), "--snapshot-every", str(every),
            "--scenario", write_json(w.path("sc.json"), {"quan": scenario}), "--out", w.path(out)]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path(out))


def snap_at(rows, tick):
    return {r["tick"]: r for r in snapshots(rows)}[tick]


def code_of(w, scenario):
    return run_headless("--mode", "quan", "--seed", "1", "--ticks", "1", "--scenario",
                        write_json(w.path("bad.json"), {"quan": scenario}), "--out", w.path("bad.jsonl"))[0]


class Customers(unittest.TestCase):
    def test_first_customer_on_schedule_reserves_stock(self):
        q = tuning()["quan"]
        first = q["first_customer_tick"]
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 1}}, ticks=first, every=first)
            ev = events(rows, "customer_arrived")
            self.assertEqual([(e["tick"], e["data"]) for e in ev],
                             [(first, {"customer_id": "C1", "table_id": "T1", "dish_id": DISH})])
            c = snap_at(rows, first)["customers"][0]
            self.assertEqual(c["reserved"], {"ca_loc": 1})
            self.assertEqual(c["patience_ticks_left"], int(q["patience_s"] * 60))
            self.assertEqual(snap_at(rows, first)["stock"], {"ca_loc": 1}, "giữ chỗ chưa trừ kho")

    def test_no_dish_when_stock_cannot_cook_anything(self):
        first = tuning()["quan"]["first_customer_tick"]
        with Workdir() as w:
            rows = run_q(w, {"stock": {"bong_sung": 1}}, ticks=first, every=first)
            self.assertEqual([e["data"] for e in events(rows, "no_dish")], [{"table_id": "T1"}])
            self.assertEqual(events(rows, "customer_arrived"), [])

    def test_full_restaurant_skips_turn(self):
        first = tuning()["quan"]["first_customer_tick"]
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 2}, "customers": [{"id": "C7", "table_id": "T1", "dish_id": DISH}]},
                         ticks=first, every=first)
            self.assertEqual(events(rows, "customer_arrived"), [])
            self.assertEqual(events(rows, "no_dish"), [])

    def test_new_ids_continue_after_scenario_ids(self):
        first = tuning()["quan"]["first_customer_tick"]
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 2}, "customers": [{"id": "C7", "table_id": "T1", "dish_id": DISH,
                                                                    "patience_ticks_left": 1}]},
                         ticks=first, every=first)
            self.assertEqual(events(rows, "customer_arrived")[0]["data"]["customer_id"], "C8")

    def test_customer_leaves_and_reputation_drops(self):
        q = tuning()["quan"]
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 1}, "random_customers": False,
                             "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "patience_ticks_left": 3}]},
                         ticks=5)
            left = events(rows, "customer_left")
            self.assertEqual([e["tick"] for e in left], [3])
            want = q["reputation_initial"] + q["left_reputation_delta"]
            self.assertEqual(left[0]["data"]["reputation"], want)
            s = snap_at(rows, 3)
            self.assertEqual(s["customers"], [])
            self.assertEqual(s["tables"][0]["customer_id"], None)
            self.assertEqual(s["reputation"], want)

    def test_reputation_clamped_at_min(self):
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 1}, "random_customers": False, "reputation": 0.2,
                             "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "patience_ticks_left": 1}]},
                         ticks=2)
            self.assertEqual(snap_at(rows, 2)["reputation"], tuning()["quan"]["reputation_min"])

    def test_random_customers_deterministic(self):
        with Workdir() as w:
            sc = {"stock": {"ca_loc": 3, "bong_sung": 4, "ca_linh": 3, "bong_dien_dien": 1}}
            run_q(w, sc, ticks=3000, every=60, seed=9, out="a.jsonl")
            run_q(w, sc, ticks=3000, every=60, seed=9, out="b.jsonl")
            with open(w.path("a.jsonl"), "rb") as a, open(w.path("b.jsonl"), "rb") as b:
                self.assertEqual(a.read(), b.read())


class Kitchen(unittest.TestCase):
    def test_cook_then_ready_then_pick(self):
        cook = int(tuning()["menu"][DISH]["cook_s"] * 60)
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 1}, "random_customers": False, "player": {"pos": [2, 7]},
                             "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH}]},
                         [{"tick": 0, "interact": True}, {"tick": 1, "interact": False},
                          {"tick": cook + 1, "interact": True}], ticks=cook + 2)
            started = events(rows, "cook_started")
            self.assertEqual(started[0]["data"], {"stove_id": "B1", "dish_id": DISH, "customer_id": "C1"})
            s1 = snap_at(rows, 1)
            self.assertEqual(s1["stock"], {}, "bắt đầu nấu mới trừ kho")
            self.assertEqual(s1["customers"][0]["reserved"], {})
            self.assertEqual(s1["stoves"][0]["state"], "cooking")
            self.assertEqual([e["tick"] for e in events(rows, "dish_ready")], [cook + 1])
            self.assertEqual([e["tick"] for e in events(rows, "dish_picked")], [cook + 2])
            last = snap_at(rows, cook + 2)
            self.assertEqual(last["hand"], DISH)
            self.assertEqual(last["stoves"][0]["state"], "idle")

    def test_idle_stove_without_orders_does_nothing(self):
        with Workdir() as w:
            rows = run_q(w, {"stock": {"ca_loc": 1}, "random_customers": False, "player": {"pos": [2, 7]}},
                         [{"tick": 0, "interact": True}], ticks=2)
            self.assertEqual(events(rows, "cook_started"), [])

    def test_stove_wins_tie_over_table(self):
        with Workdir() as w:
            rows = run_q(w, {"random_customers": False, "player": {"pos": [3, 8]}, "tables": [{"id": "T1", "pos": [4, 8]}],
                             "stoves": [{"id": "B1", "state": "ready", "dish": DISH}]},
                         [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual([e["name"] for e in rows if e["type"] == "event"], ["dish_picked"])


class Service(unittest.TestCase):
    def serve(self, patience):
        with Workdir() as w:
            sc = {"random_customers": False, "hand": DISH, "player": {"pos": [9, 2.5]},
                  "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "patience_ticks_left": patience,
                                "reserved": {}}]}
            eat = int(tuning()["quan"]["eat_s"] * 60)
            return run_q(w, sc, [{"tick": 0, "interact": True}], ticks=eat + 2, every=eat + 2), eat

    def test_served_fast_pays_price_and_tip(self):
        t = tuning()
        q, price = t["quan"], t["menu"][DISH]["price"]
        rows, eat = self.serve(int(q["patience_s"] * 60))
        self.assertEqual(events(rows, "served")[0]["data"], {"customer_id": "C1", "table_id": "T1", "dish_id": DISH})
        paid = events(rows, "paid")
        tip = int(price * q["tip_rate"])
        self.assertEqual(paid[0]["tick"], 1 + eat)
        self.assertEqual(paid[0]["data"]["price"], price)
        self.assertEqual(paid[0]["data"]["tip"], tip)
        end = rows[-1]
        self.assertEqual(end["money"], price + tip)
        self.assertEqual(end["earned"], price + tip)
        self.assertAlmostEqual(end["reputation"], q["reputation_initial"] + q["tip_reputation"])
        self.assertEqual(end["score"], price + tip + t["score"]["reputation_multiplier"] * int(end["reputation"]))

    def test_served_late_pays_no_tip(self):
        t = tuning()
        rows, _ = self.serve(100)
        paid = events(rows, "paid")[0]["data"]
        self.assertEqual(paid["tip"], 0)
        self.assertEqual(rows[-1]["reputation"], t["quan"]["reputation_initial"])

    def test_wrong_dish_is_not_served(self):
        with Workdir() as w:
            rows = run_q(w, {"random_customers": False, "hand": "goi_bong_sung", "player": {"pos": [9, 2.5]},
                             "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "reserved": {}}]},
                         [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual(events(rows, "served"), [])

    def test_shift_ends_with_quan_end(self):
        with Workdir() as w:
            rows = run_q(w, {"time_left_ticks": 2}, ticks=10)
            end = events(rows, "quan_end")
            self.assertEqual(end[0]["tick"], 2)
            self.assertEqual(rows[-1]["reason"], "time")


class ScenarioConflicts(unittest.TestCase):
    def test_conflicts_exit_2(self):
        bad = [
            {"stock": {"ca_loc": 0}, "customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH}]},
            {"customers": [{"id": "C1", "table_id": "T1", "dish_id": "pho"}]},
            {"customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "state": "eating", "eat_ticks_left": 5}]},
            {"customers": [{"id": "C1", "table_id": "T1", "dish_id": DISH, "state": "sleeping"}]},
            {"stoves": [{"id": "B1", "state": "cooking", "cook_ticks_left": 5}]},
            {"stoves": [{"id": "B1", "state": "idle", "dish": DISH}]},
            {"hand": "pho"},
            {"reputation": 9},
        ]
        with Workdir() as w:
            for sc in bad:
                self.assertEqual(code_of(w, sc), 2, sc)

    def test_eating_customer_from_scenario_pays(self):
        with Workdir() as w:
            rows = run_q(w, {"random_customers": False, "customers": [
                {"id": "C1", "table_id": "T1", "dish_id": DISH, "state": "eating", "eat_ticks_left": 2,
                 "price": 60, "tip": 0}]}, ticks=3)
            self.assertEqual([(e["tick"], e["data"]["price"]) for e in events(rows, "paid")], [(2, 60)])


if __name__ == "__main__":
    unittest.main()
