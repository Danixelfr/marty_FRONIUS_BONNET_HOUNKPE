import unittest
from unittest.mock import patch
from server.http_server import HTTPServer


class TestHTTPServer(unittest.TestCase):
    def test_server_init(self):
        with patch("server.http_server.BaseHTTPServer"):
            server = HTTPServer(host="localhost", port=9090)
            self.assertEqual(server.host, "localhost")
            self.assertEqual(server.port, 9090)


if __name__ == "__main__":
    unittest.main()
