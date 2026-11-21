"""Luật buổi sáng (gather) của nhóm — lát 1 (oxy, ngạt, Máu) và lát 2 (hái, bắt cá, giỏ).

Test HỘP ĐEN: chỉ chạy headless_cmd rồi đọc JSONL / file kho. Giả định luật ghi ở docs/clarify.md (#3–#6).
"""

import json
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


def tuning():
    with open("game.contract.json", encoding="utf-8") as f:
        return json.load(f)["tuning"]["gather"]


def run_g(w, scenario, inputs=None, ticks=10, every=1, inv_out=None):
    args = ["--mode", "gather", "--seed", "1", "--ticks", str(ticks), "--snapshot-every", str(every),
            "--scenario", write_json(w.path("sc.json"), {"gather": scenario}), "--out", w.path("o.jsonl")]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), frames(*inputs))]
    if inv_out:
        args += ["--inventory-out", inv_out]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path("o.jsonl"))


def snap_at(rows, tick):
    return {r["tick"]: r for r in snapshots(rows)}[tick]


class Oxygen(unittest.TestCase):
    def test_dive_and_surface_events(self):
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [20, 0]}, "random_fish": False},
                         [{"tick": 0, "move": [0, 1]}, {"tick": 30, "move": [0, -1]}], ticks=80)
            dive, surf = events(rows, "dive"), events(rows, "surface")
            self.assertEqual(len(dive), 1)
            self.assertEqual(len(surf), 1)
            self.assertGreater(dive[0]["data"]["pos"][1], tuning()["surface_depth"])
            self.assertLessEqual(surf[0]["data"]["pos"][1], tuning()["surface_depth"])
            self.assertLess(dive[0]["tick"], surf[0]["tick"])

    def test_oxygen_drains_underwater_and_refills_at_surface(self):
        g = tuning()
        omax = int(g["oxygen_max_s"] * 60)
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [50, 10]}}, ticks=10)
            self.assertEqual(snap_at(rows, 10)["player"]["oxygen_ticks"], omax - 10)
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [50, 0], "oxygen_ticks": 100}}, ticks=2)
            self.assertEqual(snap_at(rows, 1)["player"]["oxygen_ticks"], 100 + g["oxygen_refill_per_tick"])
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [50, 0], "oxygen_ticks": omax - 1}}, ticks=1)
            self.assertEqual(snap_at(rows, 1)["player"]["oxygen_ticks"], omax, "kẹp ở oxy tối đa")

    def test_oxygen_empty_then_choke(self):
        g = tuning()
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [50, 10], "oxygen_ticks": 1}}, ticks=g["choke_interval_ticks"] + 1)
            empty = events(rows, "oxygen_empty")
            self.assertEqual([e["tick"] for e in empty], [1])
            choke = events(rows, "choke")
            self.assertEqual([e["tick"] for e in choke], [g["choke_interval_ticks"]])
            self.assertEqual(choke[0]["data"]["hp"], g["hp_max"] - 1)
            self.assertEqual(snap_at(rows, g["choke_interval_ticks"])["player"]["zero_oxy_ticks"], 0)

    def test_surface_resets_choke_counter(self):
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [50, 1], "oxygen_ticks": 0, "zero_oxy_ticks": 30}},
                         [{"tick": 0, "move": [0, -1]}], ticks=20)
            self.assertEqual(events(rows, "choke"), [])
            self.assertEqual(snap_at(rows, 20)["player"]["zero_oxy_ticks"], 0)

    def test_faint_loses_hold_and_writes_empty_inventory(self):
        g = tuning()
        with Workdir() as w:
            inv = w.path("inv.json")
            rows = run_g(w, {"player": {"pos": [50, 10], "oxygen_ticks": 0, "hp": 1,
                                        "zero_oxy_ticks": g["choke_interval_ticks"] - 1},
                             "hold": ["ca_loc", "bong_sung"]}, ticks=100, inv_out=inv)
            names = [r["name"] for r in rows if r["type"] == "event"]
            self.assertEqual(names, ["choke", "faint", "gather_end"])
            end = events(rows, "gather_end")[0]
            self.assertEqual(end["tick"], 1)
            self.assertEqual(end["data"], {"reason": "fainted", "inventory": {"items": {}}})
            self.assertEqual(rows[-1]["reason"], "fainted")
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": {}})


class Harvest(unittest.TestCase):
    def test_harvest_nearest_ready_node_at_surface(self):
        g = tuning()
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [44, 0]}}, [{"tick": 0, "interact": True}, {"tick": 1, "interact": False},
                                                           {"tick": 2, "interact": True}], ticks=4)
            ev = events(rows, "gather")
            self.assertEqual(len(ev), 1, "nút vừa hái chưa mọc lại")
            self.assertEqual(ev[0]["data"], {"node_id": "N3", "kind": "bong_sung", "count": g["node_yield"]})
            s = snap_at(rows, 1)
            self.assertEqual(s["hold"], ["bong_sung"] * g["node_yield"])
            n3 = [n for n in s["nodes"] if n["id"] == "N3"][0]
            self.assertFalse(n3["ready"])
            self.assertEqual(n3["regrow_ticks"], int(g["regrow_s"] * 60))

    def test_tie_breaks_by_smaller_id(self):
        nodes = [{"id": "N2", "kind": "bong_sung", "pos": [11, 0]}, {"id": "N1", "kind": "bong_dien_dien", "pos": [9, 0]}]
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [10, 0]}, "nodes": nodes}, [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual(events(rows, "gather")[0]["data"]["node_id"], "N1")

    def test_no_harvest_underwater(self):
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [44, 1.5]}}, [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual(events(rows, "gather"), [])

    def test_hold_full_on_harvest(self):
        g = tuning()
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [44, 0]}, "hold": ["ca_loc"] * g["hold_capacity"]},
                         [{"tick": 0, "interact": True}], ticks=1)
            self.assertEqual(events(rows, "gather"), [])
            full = events(rows, "hold_full")
            self.assertEqual(full[0]["data"], {"source": "N3", "kind": "bong_sung", "need": g["node_yield"], "free": 0})
            self.assertTrue([n for n in snap_at(rows, 1)["nodes"] if n["id"] == "N3"][0]["ready"])

    def test_node_regrown_event(self):
        with Workdir() as w:
            rows = run_g(w, {"nodes": [{"id": "N1", "kind": "bong_sung", "pos": [40, 0], "regrow_ticks": 2}]}, ticks=3)
            self.assertEqual([(e["tick"], e["data"]) for e in events(rows, "node_regrown")], [(2, {"node_id": "N1"})])


class Catch(unittest.TestCase):
    def test_catch_school_underwater(self):
        g = tuning()
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [45, 9]}}, [{"tick": 0, "catch": True}], ticks=2)
            ev = events(rows, "fish_caught")
            self.assertEqual(ev[0]["data"], {"fish_id": "F3", "kind": "ca_linh", "count": g["fish_yield"]["ca_linh"]})
            s = snap_at(rows, 1)
            self.assertNotIn("F3", [f["id"] for f in s["fish"]])
            self.assertEqual(s["hold"], ["ca_linh"] * g["fish_yield"]["ca_linh"])
            self.assertEqual(s["player"]["catch_cd_ticks"], int(round(g["catch_cooldown_s"] * 60)))

    def test_cooldown_blocks_second_catch(self):
        fish = [{"id": "F1", "kind": "ca_loc", "pos": [20, 5]}, {"id": "F2", "kind": "ca_loc", "pos": [21, 5]}]
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [20.5, 5]}, "fish": fish},
                         [{"tick": 0, "catch": True}, {"tick": 1, "catch": False}, {"tick": 2, "catch": True}], ticks=4)
            self.assertEqual([e["data"]["fish_id"] for e in events(rows, "fish_caught")], ["F1"])

    def test_catch_ignored_at_surface(self):
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [15, 0]}, "fish": [{"id": "F1", "kind": "ca_loc", "pos": [15, 1]}]},
                         [{"tick": 0, "catch": True}], ticks=1)
            self.assertEqual(events(rows, "fish_caught"), [])
            self.assertEqual(snap_at(rows, 1)["player"]["catch_cd_ticks"], 0)

    def test_hold_full_keeps_school(self):
        g = tuning()
        cap = g["hold_capacity"]
        with Workdir() as w:
            rows = run_g(w, {"player": {"pos": [45, 9]}, "hold": ["bong_sung"] * (cap - 1)},
                         [{"tick": 0, "catch": True}], ticks=1)
            self.assertEqual(events(rows, "fish_caught"), [])
            self.assertEqual(events(rows, "hold_full")[0]["data"]["source"], "F3")
            self.assertIn("F3", [f["id"] for f in snap_at(rows, 1)["fish"]])


class Run(unittest.TestCase):
    def test_full_morning_to_inventory(self):
        """Lặn bắt F1, nổi lên hái N1, bơi về bến cập bến: kho có đúng những gì đã nhặt."""
        with Workdir() as w:
            inv = w.path("inv.json")
            inputs = [{"tick": 0, "move": [0.933, 0.359]}, {"tick": 205, "move": [0, 0]}, {"tick": 206, "catch": True},
                      {"tick": 207, "move": [-0.287, -0.958], "catch": False}, {"tick": 300, "move": [0, 0]},
                      {"tick": 301, "interact": True}, {"tick": 302, "move": [-1, 0], "interact": False},
                      {"tick": 500, "move": [0, 0]}, {"tick": 501, "interact": True}]
            rows = run_g(w, {"player": {"pos": [2, 0]}}, inputs, ticks=600, every=10, inv_out=inv)
            names = [r["name"] for r in rows if r["type"] == "event"]
            self.assertEqual(names, ["dive", "fish_caught", "surface", "gather", "gather_end"])
            end = events(rows, "gather_end")[0]
            self.assertEqual(end["data"], {"reason": "docked",
                                           "inventory": {"items": {"bong_dien_dien": 1, "ca_linh": 3}}})
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), end["data"]["inventory"])


if __name__ == "__main__":
    unittest.main()
