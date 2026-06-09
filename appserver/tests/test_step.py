import unittest

from server.registry import registry
from server.battle_config import battle_config
from server.routes.step import handle_post_step


SPEC_RULES = {
    "R": [
        {"conditions": "ALU+ARU", "score": 2},
        {"conditions": "ALU,ARU", "score": 1},
        {"conditions": "ALB,ARB", "score": 1},
        {"conditions": "XNG", "score": 3},
        {"conditions": "XSD", "score": -2},
        {"conditions": "XNT", "score": -1},
    ],
    "B": [
        {"conditions": "ALB,ARB,ALU,ARU", "score": -1},
        {"conditions": "XSD", "score": 2},
    ],
}


class FakeHandler:
    def __init__(self, body):
        self._body = body
        self.status = None
        self.payload = None

    def _read_body(self):
        return self._body

    def send_json(self, code, data):
        self.status = code
        self.payload = data


class TestStep(unittest.TestCase):

    def setUp(self):
        registry._robots.clear()
        battle_config.load(mvs=10, rules=SPEC_RULES, path="test.battle")

    def _ready_robot(self):
        rid = registry.register()
        registry.update(rid, state="dancing", nb_steps_required=10, nb_steps_done=0, score=0)
        return rid

    def test_red_two_arms_anger(self):
        rid = self._ready_robot()
        h = FakeHandler({"rid": rid, "col": "R", "arm": "ALU+ARU", "exp": "XNG"})
        handle_post_step(h)
        self.assertEqual(h.status, 200)
        self.assertEqual(h.payload, 6)

    def test_blue_sad(self):
        rid = self._ready_robot()
        h = FakeHandler({"rid": rid, "col": "B", "arm": "", "exp": "XSD"})
        handle_post_step(h)
        self.assertEqual(h.payload, 2)

    def test_score_accumulates(self):
        rid = self._ready_robot()
        handle_post_step(FakeHandler({"rid": rid, "col": "R", "arm": "ALU+ARU", "exp": "XNG"}))
        handle_post_step(FakeHandler({"rid": rid, "col": "B", "arm": "", "exp": "XSD"}))
        robot = registry.get(rid)
        self.assertEqual(robot["score"], 8)
        self.assertEqual(robot["nb_steps_done"], 2)

    def test_returns_step_points_not_total(self):
        rid = self._ready_robot()
        handle_post_step(FakeHandler({"rid": rid, "col": "R", "arm": "ALU+ARU", "exp": "XNG"}))
        h = FakeHandler({"rid": rid, "col": "B", "arm": "", "exp": "XSD"})
        handle_post_step(h)
        self.assertEqual(h.payload, 2)

    def test_unknown_rid_404(self):
        h = FakeHandler({"rid": "ZZZZZZ", "col": "R"})
        handle_post_step(h)
        self.assertEqual(h.status, 404)

    def test_missing_rid_400(self):
        h = FakeHandler({"col": "R"})
        handle_post_step(h)
        self.assertEqual(h.status, 400)

    def test_missing_col_400(self):
        rid = self._ready_robot()
        h = FakeHandler({"rid": rid})
        handle_post_step(h)
        self.assertEqual(h.status, 400)


if __name__ == "__main__":
    unittest.main()
