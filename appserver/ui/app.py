import sys
import threading
import logging
from PyQt6.QtWidgets import QApplication
from server.http_server import DanceBattleServer
from ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def run_app(host="0.0.0.0", port=8080):
    app = QApplication(sys.argv)

    server = DanceBattleServer(host=host, port=port)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()

    window = MainWindow()
    window.show()

    code = app.exec()
    server.stop()
    return code
