from http.server import HTTPServer as BaseHTTPServer
from server.handler import RequestHandler


class HTTPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self._server = BaseHTTPServer((host, port), RequestHandler)

    def start(self):
        print(f"Serveur démarré sur http://{self.host}:{self.port}")
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()
