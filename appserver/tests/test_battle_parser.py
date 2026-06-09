import os

from server.battle.parser import parse_battle, parse_battle_file
from server.battle.evaluator import compute_points

SAMPLE = os.path.join(os.path.dirname(__file__), "sample.battle")


def test_parse_mvs():
    mvs, rules = parse_battle_file(SAMPLE)
    assert mvs == 10


def test_parse_colors():
    mvs, rules = parse_battle_file(SAMPLE)
    assert set(rules) == {"N", "B", "R"}


def test_red_rules_content():
    mvs, rules = parse_battle_file(SAMPLE)
    assert {"conditions": "ALU+ARU", "score": 2} in rules["R"]
    assert {"conditions": "XNG", "score": 3} in rules["R"]
    assert {"conditions": "XSD", "score": -2} in rules["R"]


def test_parser_feeds_evaluator():
    mvs, rules = parse_battle_file(SAMPLE)
    assert compute_points(rules["R"], "ALU+ARU", "XNG") == 6
    assert compute_points(rules["B"], "", "XSD") == 2


def test_inline_parse():
    mvs, rules = parse_battle("MVS 5\n[R]\nALU=2\n")
    assert mvs == 5
    assert rules["R"] == [{"conditions": "ALU", "score": 2}]


def test_no_mvs_defaults_zero():
    mvs, rules = parse_battle("[R]\nALU=1\n")
    assert mvs == 0
