import threading
import logging
from PyQt6.QtWidgets import QApplication
from server.http_server import DanceBattleServer
from ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def run_app(host="0.0.0.0", port=8080):
    app = QApplication([])

    window = MainWindow()
    window.show()

    server = DanceBattleServer(host=host, port=port)
    threading.Thread(target=server.start, daemon=True).start()

    code = app.exec()
    server.stop()
    return code
