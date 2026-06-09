import unittest

from server.registry import registry
from server.routes.score import handle_get_score
from server.routes.bye import handle_post_bye


class FakeHandler:
    def __init__(self, body=None, path=""):
        self._body = body or {}
        self.path = path
        self.status = None
        self.payload = None

    def _read_body(self):
        return self._body

    def send_json(self, code, data):
        self.status = code
        self.payload = data


class TestScoreBye(unittest.TestCase):

    def setUp(self):
        registry._robots.clear()

    def _robot_with_score(self, score):
        rid = registry.register()
        registry.update(rid, score=score, state="dancing", nb_steps_done=2)
        return rid

    def test_score_returns_int(self):
        rid = self._robot_with_score(8)
        h = FakeHandler(path=f"/score?rid={rid}")
        handle_get_score(h)
        self.assertEqual(h.status, 200)
        self.assertIsInstance(h.payload, int)
        self.assertEqual(h.payload, 8)

    def test_score_missing_rid_400(self):
        h = FakeHandler(path="/score")
        handle_get_score(h)
        self.assertEqual(h.status, 400)

    def test_score_unknown_rid_404(self):
        h = FakeHandler(path="/score?rid=ZZZZZZ")
        handle_get_score(h)
        self.assertEqual(h.status, 404)

    def test_bye_marks_disconnected(self):
        rid = self._robot_with_score(8)
        handle_post_bye(FakeHandler(body={"rid": rid}))
        robot = registry.get(rid)
        self.assertEqual(robot["state"], "disconnected")
        self.assertFalse(robot["active"])
        self.assertIsNotNone(robot["disconnected_at"])

    def test_bye_does_not_delete_robot(self):
        rid = self._robot_with_score(8)
        handle_post_bye(FakeHandler(body={"rid": rid}))
        self.assertIsNotNone(registry.get(rid))

    def test_score_readable_after_bye(self):
        rid = self._robot_with_score(8)
        handle_post_bye(FakeHandler(body={"rid": rid}))
        h = FakeHandler(path=f"/score?rid={rid}")
        handle_get_score(h)
        self.assertEqual(h.payload, 8)

    def test_bye_returns_final_score(self):
        rid = self._robot_with_score(8)
        h = FakeHandler(body={"rid": rid})
        handle_post_bye(h)
        self.assertEqual(h.status, 200)
        self.assertEqual(h.payload["final_score"], 8)

    def test_bye_unknown_rid_tolerant(self):
        h = FakeHandler(body={"rid": "ZZZZZZ"})
        handle_post_bye(h)
        self.assertEqual(h.status, 200)

    def test_bye_missing_rid_400(self):
        h = FakeHandler(body={})
        handle_post_bye(h)
        self.assertEqual(h.status, 400)


if __name__ == "__main__":
    unittest.main()
