import logging
import threading
from http.server import ThreadingHTTPServer
from .handler import RequestHandler

logger = logging.getLogger(__name__)


class DanceBattleServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self._httpd = None
        self._lock = threading.Lock()

    def start(self):
        self._httpd = ThreadingHTTPServer((self.host, self.port), RequestHandler)
        logger.info(f"Serveur démarré sur http://{self.host}:{self.port}")
        try:
            self._httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Arrêt demandé (Ctrl+C)")
        finally:
            self.stop()

    def stop(self):
        with self._lock:
            httpd = self._httpd
            self._httpd = None
        if httpd is None:
            return
        httpd.shutdown()
        httpd.server_close()
        logger.info("Serveur arrêté proprement")
