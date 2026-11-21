"""Kiểm dải tuning của nhóm (Phase 2): bếp/bàn, carry_limit, uy tín, công thức món.

Unit test của starter Python (gọi thẳng validate_tuning); đổi ngôn ngữ thì viết lại bằng ngôn ngữ của nhóm.
"""

import copy
import json
import os
import unittest

from chonoi.contract import validate_tuning
from chonoi.errors import BadInput
from helpers import ROOT


def base():
    with open(os.path.join(ROOT, "game.contract.json"), encoding="utf-8") as f:
        return json.load(f)["tuning"]


class TuningRanges(unittest.TestCase):
    def test_shipped_contract_is_valid(self):
        validate_tuning(base())

    def test_bad_values_rejected(self):
        cases = [
            ("quan", "carry_limit", 2),
            ("quan", "stoves", []),
            ("quan", "tables", [{"id": "T1", "pos": [99, 2]}]),
            ("quan", "tables", [{"id": "T1", "pos": [1, 1]}, {"id": "T1", "pos": [2, 2]}]),
            ("quan", "start_pos", [20, 5]),
            ("quan", "reputation_initial", 7),
            ("quan", "reputation_min", 5),
        ]
        for block, key, val in cases:
            t = copy.deepcopy(base())
            t[block][key] = val
            with self.assertRaises(BadInput, msg=(key, val)):
                validate_tuning(t)

    def test_bad_recipe_and_score_rejected(self):
        for mutate in (lambda t: t["menu"]["goi_bong_sung"].update(recipe={}),
                       lambda t: t["menu"]["goi_bong_sung"].update(recipe={"ca_la_lung": 1}),
                       lambda t: t["menu"]["goi_bong_sung"].update(recipe={"bong_sung": 0}),
                       lambda t: t["score"].update(reputation_multiplier=-1)):
            t = copy.deepcopy(base())
            mutate(t)
            with self.assertRaises(BadInput):
                validate_tuning(t)


if __name__ == "__main__":
    unittest.main()
