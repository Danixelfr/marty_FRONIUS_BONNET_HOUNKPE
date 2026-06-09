import unittest
from unittest.mock import patch

# Ajustement: le code du serveur est exposé via appserver/server.
# Le test doit donc importer depuis le package appserver.
from appserver.server.http_server import DanceBattleServer


class TestHTTPServer(unittest.TestCase):
    def test_server_init(self):
        server = DanceBattleServer(host="localhost", port=9090)
        self.assertEqual(server.host, "localhost")
        self.assertEqual(server.port, 9090)



if __name__ == "__main__":
    unittest.main()
