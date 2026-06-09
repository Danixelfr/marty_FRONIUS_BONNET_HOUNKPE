from server.battle.evaluator import compute_points, parse_arms

RED_RULES = [
    ("AND", ["ALU", "ARU"], 2),
    ("OR", ["ALU", "ARU"], 1),
    ("OR", ["ALB", "ARB"], 1),
    ("SINGLE", ["XNG"], 3),
    ("SINGLE", ["XSD"], -2),
    ("SINGLE", ["XNT"], -1),
]

RED_RULES_DICT = [
    {"conditions": "ALU+ARU", "score": 2},
    {"conditions": "ALU,ARU", "score": 1},
    {"conditions": "ALB,ARB", "score": 1},
    {"conditions": "XNG", "score": 3},
    {"conditions": "XSD", "score": -2},
    {"conditions": "XNT", "score": -1},
]


def test_two_arms_up_with_anger():
    assert compute_points(RED_RULES, "ALU+ARU", "XNG") == 6


def test_spec_example_dict_format():
    assert compute_points(RED_RULES_DICT, "ALU+ARU", "XNG") == 6


def test_or_counts_once():
    rules = [("OR", ["ALU", "ARU"], 1)]
    assert compute_points(rules, "ALU+ARU", "XNT") == 1


def test_and_requires_all():
    rules = [("AND", ["ALU", "ARU"], 5)]
    assert compute_points(rules, "ALU", "XNT") == 0
    assert compute_points(rules, "ALU+ARU", "XNT") == 5


def test_negative_points():
    rules = [("SINGLE", ["XSD"], -3)]
    assert compute_points(rules, "", "XSD") == -3


def test_empty_arm():
    rules = [("SINGLE", ["XNG"], 2)]
    assert compute_points(rules, "", "XNG") == 2


def test_no_rules():
    assert compute_points([], "ALU", "XNT") == 0


def test_blue_section_sad():
    blue = [
        {"conditions": "ALB,ARB,ALU,ARU", "score": -1},
        {"conditions": "XSD", "score": 2},
    ]
    assert compute_points(blue, "", "XSD") == 2


def test_parse_arms():
    assert parse_arms("") == set()
    assert parse_arms("ALU") == {"ALU"}
    assert parse_arms("ALU+ARU") == {"ALU", "ARU"}
    assert parse_arms("ALU+ARU+ALB") == {"ALU", "ARU", "ALB"}
