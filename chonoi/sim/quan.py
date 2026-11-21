"""Buổi tối — Mở Quán. KHUNG: đi lại, chặn biên, đồng hồ, kho nạp từ file/scenario.

Nhóm ChuToa đã viết (Phase 1; giả định chi tiết ở docs/clarify.md #7–#11, test ở tests/test_quan_rules.py):
  ĐÃ LÀM (lát 3): khách đến theo lịch, chọn món nấu được, giữ chỗ nguyên liệu, kiên nhẫn,
                  bỏ đi (customer_left), no_dish, vòng đời khách.
  ĐÃ LÀM (lát 4): interact tại bếp/bàn (cook_started, dish_ready, dish_picked, served),
                  ăn xong trả tiền (paid), boa, uy tín, hết ca (quan_end).

Thứ tự một bước: đồng hồ -> bếp (nấu, chín) -> khách (kiên nhẫn, ăn xong) -> đi lại -> tối đa MỘT interact
-> khách mới theo lịch -> hết ca.
Kho: `stock` là nguyên liệu còn trong bếp; `reserved` của khách là phần đã giữ chỗ (chưa trừ khỏi stock).
Lúc bắt đầu nấu mới trừ khỏi stock và xóa phần giữ chỗ của khách được nấu cho.
"""

import math

from ..errors import BadInput
from ..ids import id_key, sort_by_id
from .ramp import ramp_velocity

TICK = 60.0


def _ticks(seconds):
    return max(1, int(round(seconds * TICK)))


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        # kho: --inventory HOẶC scenario.stock (cả hai -> cli đã báo mã 2)
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.duration_ticks = int(round(t["duration_s"] * TICK))
        self.time_left_ticks = scenario.get("time_left_ticks", self.duration_ticks)
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.random_customers = scenario.get("random_customers", True)
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        # khách dựng sẵn từ scenario; khách đang đợi mà không ghi `reserved` thì suy ra = công thức món
        self.customers = []
        for c in scenario.get("customers", []):
            state = c.get("state", "waiting")
            cust = dict(c, state=state, patience_ticks_left=c.get("patience_ticks_left", self._patience_max()))
            if "reserved" in c:
                cust["reserved"] = dict(c["reserved"])
            else:
                cust["reserved"] = dict(self.menu[c["dish_id"]]["recipe"]) if state == "waiting" else {}
            self.customers.append(cust)
        for e in self.customers:
            ids.reserve(e["id"])
        self._check_reservations()
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _patience_max(self):
        return _ticks(self.t["patience_s"])

    def _check_reservations(self):
        """Mâu thuẫn mức luật: tổng nguyên liệu khách giữ chỗ không được vượt kho (mã 2)."""
        for k, v in self._reserved_total().items():
            if v > self.stock.get(k, 0):
                raise BadInput(f"khách giữ chỗ {v} {k} nhưng kho chỉ có {self.stock.get(k, 0)}")

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        now = self.duration_ticks - self.time_left_ticks  # tick đã trôi của ca, sau bước này
        self._tick_stoves(events)
        self._tick_customers(events)
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        self._spawn(now, events)
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    # --- lát 3: khách ------------------------------------------------------------
    def _reserved_total(self):
        tot = {}
        for c in self.customers:
            for k, v in c.get("reserved", {}).items():
                tot[k] = tot.get(k, 0) + v
        return tot

    def _cookable(self):
        """Món nấu được bằng phần kho chưa bị giữ chỗ, theo thứ tự id món."""
        res = self._reserved_total()
        free = {k: self.stock.get(k, 0) - res.get(k, 0) for k in set(self.stock) | set(res)}
        return [d for d in sorted(self.menu)
                if all(free.get(k, 0) >= n for k, n in self.menu[d]["recipe"].items())]

    def _spawn(self, now, events):
        if not self.random_customers:
            return
        first = int(self.t["first_customer_tick"])
        every = _ticks(self.t["customer_interval_s"])
        if now < first or (now - first) % every != 0:
            return
        busy = {c["table_id"] for c in self.customers}
        free_tables = [tb for tb in self.tables if tb["id"] not in busy]
        if not free_tables:
            return  # quán kín bàn: bỏ lượt, không sự kiện (clarify #7)
        table = free_tables[0]
        dishes = self._cookable()
        if not dishes:
            events.append(("no_dish", {"table_id": table["id"]}))
            return
        dish = dishes[self.rng.get("customer_dish").randrange(len(dishes))]
        cid = self.ids.new("C")
        self.customers.append({"id": cid, "table_id": table["id"], "dish_id": dish, "state": "waiting",
                               "patience_ticks_left": self._patience_max(),
                               "reserved": dict(self.menu[dish]["recipe"])})
        events.append(("customer_arrived", {"customer_id": cid, "table_id": table["id"], "dish_id": dish}))

    def _tick_customers(self, events):
        keep = []
        for c in sort_by_id(self.customers):
            if c["state"] == "waiting":
                c["patience_ticks_left"] -= 1
                if c["patience_ticks_left"] <= 0:
                    self._add_reputation(self.t["left_reputation_delta"])
                    events.append(("customer_left", {"customer_id": c["id"], "table_id": c["table_id"],
                                                     "dish_id": c["dish_id"], "reputation": self.reputation}))
                    continue  # bỏ đi: phần giữ chỗ tự được trả (khách không còn trong danh sách)
            elif c["state"] == "eating":
                c["eat_ticks_left"] -= 1
                if c["eat_ticks_left"] <= 0:
                    self._pay(c, events)
                    continue
            keep.append(c)
        self.customers = keep

    # --- lát 4: bếp, bưng, phục vụ, tiền -----------------------------------------
    def _tick_stoves(self, events):
        for s in self.stoves:
            if s["state"] == "cooking":
                s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
                if s["cook_ticks_left"] == 0:
                    s["state"] = "ready"
                    s["ready_ticks"] = 0
                    events.append(("dish_ready", {"stove_id": s["id"], "dish_id": s["dish"]}))
            elif s["state"] == "ready":
                s["ready_ticks"] += 1  # burn_s = null ở Phase 1: món chín không cháy

    def _interact(self, events):
        r = self.t["interact_radius"]
        cands = []
        for s in self.stoves:
            d = math.dist(self.pos, s["pos"])
            if d <= r:
                cands.append((d, 0, s["id"], "stove", s))
        for tb in self.tables:
            d = math.dist(self.pos, tb["pos"])
            if d <= r:
                cands.append((d, 1, tb["id"], "table", tb))
        if not cands:
            return
        cands.sort(key=lambda c: (c[0], c[1], id_key(c[2])))
        _, _, _, kind, obj = cands[0]
        if kind == "stove":
            self._use_stove(obj, events)
        else:
            self._use_table(obj, events)

    def _next_order(self):
        """Khách đang đợi sớm nhất (id nhỏ) mà món của họ chưa có trên bếp / trên tay."""
        pending = {}
        for s in self.stoves:
            if s["state"] in ("cooking", "ready") and s["dish"]:
                pending[s["dish"]] = pending.get(s["dish"], 0) + 1
        if self.hand:
            pending[self.hand] = pending.get(self.hand, 0) + 1
        for c in sort_by_id(self.customers):
            if c["state"] != "waiting":
                continue
            if pending.get(c["dish_id"], 0) > 0:
                pending[c["dish_id"]] -= 1
                continue
            return c
        return None

    def _use_stove(self, s, events):
        if s["state"] == "idle":
            c = self._next_order()
            if c is None:
                return
            recipe = self.menu[c["dish_id"]]["recipe"]
            if any(self.stock.get(k, 0) < n for k, n in recipe.items()):
                return
            for k, n in recipe.items():
                self.stock[k] -= n
            c["reserved"] = {}
            s.update(state="cooking", dish=c["dish_id"], cook_ticks_left=_ticks(self.menu[c["dish_id"]]["cook_s"]),
                     ready_ticks=0)
            events.append(("cook_started", {"stove_id": s["id"], "dish_id": c["dish_id"], "customer_id": c["id"]}))
        elif s["state"] == "ready" and self.hand is None:  # carry_limit = 1
            self.hand = s["dish"]
            events.append(("dish_picked", {"stove_id": s["id"], "dish_id": s["dish"]}))
            s.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0)

    def _use_table(self, tb, events):
        c = next((c for c in self.customers if c["table_id"] == tb["id"]), None)
        if c is None or c["state"] != "waiting" or self.hand != c["dish_id"]:
            return
        price = int(self.menu[c["dish_id"]]["price"])
        tipped = c["patience_ticks_left"] >= self.t["tip_min_patience_ratio"] * self._patience_max()
        tip = int(math.floor(price * self.t["tip_rate"])) if tipped else 0
        c.update(state="eating", eat_ticks_left=_ticks(self.t["eat_s"]), price=price, tip=tip, reserved={})
        self.hand = None
        events.append(("served", {"customer_id": c["id"], "table_id": tb["id"], "dish_id": c["dish_id"]}))

    def _pay(self, c, events):
        amount = c.get("price", 0) + c.get("tip", 0)
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        if c.get("tip", 0) > 0:
            self._add_reputation(self.t["tip_reputation"])
        events.append(("paid", {"customer_id": c["id"], "price": c.get("price", 0), "tip": c.get("tip", 0),
                                "money": self.money, "reputation": self.reputation}))

    def _add_reputation(self, delta):
        r = self.reputation + delta
        self.reputation = min(self.t["reputation_max"], max(self.t["reputation_min"], round(r, 6)))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
