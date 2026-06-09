"""Tests de la route POST /start (M-004).

On teste directement la fonction handle_post_start avec un faux handler
qui enregistre la réponse, sans lancer de vrai serveur HTTP.

Lancer depuis le dossier `appserver/` :
    python -m unittest tests.test_start
"""
import unittest

from server.registry import registry
from server.battle_config import battle_config, BattleConfig
from server.routes.start import handle_post_start


class FakeHandler:
    """Imite le RequestHandler : capture la réponse au lieu de l'envoyer."""

    def __init__(self, body: dict):
        self._body = body
        self.status = None
        self.payload = None

    def _read_body(self) -> dict:
        return self._body

    def send_json(self, code, data):
        self.status = code
        self.payload = data


class TestStart(unittest.TestCase):

    def setUp(self):
        # On repart d'un registre et d'une config propres à chaque test
        registry._robots.clear()
        battle_config._mvs = BattleConfig.DEFAULT_MVS
        battle_config._loaded_path = None

    def test_start_returns_mvs_integer(self):
        rid = registry.register()
        h = FakeHandler({"rid": rid})
        handle_post_start(h)

        self.assertEqual(h.status, 200)
        self.assertIsInstance(h.payload, int)        # entier, pas une string
        self.assertEqual(h.payload, 10)              # MVS par défaut

    def test_start_sets_state_dancing(self):
        rid = registry.register()
        handle_post_start(FakeHandler({"rid": rid}))

        robot = registry.get(rid)
        self.assertEqual(robot["state"], "dancing")
        self.assertEqual(robot["nb_steps_required"], 10)
        self.assertEqual(robot["nb_steps_done"], 0)

    def test_start_resets_score(self):
        rid = registry.register()
        registry.update(rid, score=42, nb_steps_done=5)  # simule une danse en cours
        handle_post_start(FakeHandler({"rid": rid}))

        robot = registry.get(rid)
        self.assertEqual(robot["score"], 0)
        self.assertEqual(robot["nb_steps_done"], 0)

    def test_start_unknown_rid_returns_404(self):
        h = FakeHandler({"rid": "ZZZZZZ"})
        handle_post_start(h)

        self.assertEqual(h.status, 404)
        self.assertIn("error", h.payload)

    def test_start_missing_rid_returns_400(self):
        h = FakeHandler({})
        handle_post_start(h)

        self.assertEqual(h.status, 400)
        self.assertIn("error", h.payload)

    def test_start_uses_loaded_mvs(self):
        battle_config.load(mvs=6, rules={}, path="fake.battle")
        rid = registry.register()
        h = FakeHandler({"rid": rid})
        handle_post_start(h)

        self.assertEqual(h.payload, 6)               # MVS du .battle chargé


if __name__ == "__main__":
    unittest.main()
