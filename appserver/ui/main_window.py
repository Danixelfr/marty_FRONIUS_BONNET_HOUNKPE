from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QStatusBar, QLabel,
)
from PyQt6.QtCore import QTimer
from .robots_table import RobotsTable
from .events_log import EventsLog
from server.registry import registry
from server.battle_config import battle_config
from server.battle.parser import parse_battle_file


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dance Battle - Server")
        self.resize(1100, 700)

        self.robots_table = RobotsTable()
        self.events_log = EventsLog()
        self.btn_load_battle = QPushButton("Charger .battle")
        self.btn_load_battle.clicked.connect(self._load_battle)

        central = QWidget()
        root = QVBoxLayout(central)

        top = QHBoxLayout()
        top.addWidget(self.btn_load_battle)
        top.addStretch()
        root.addLayout(top)

        body = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("ROBOTS CONNECTES"))
        left.addWidget(self.robots_table)
        right = QVBoxLayout()
        right.addWidget(QLabel("EVENEMENTS (live)"))
        right.addWidget(self.events_log)
        body.addLayout(left, 2)
        body.addLayout(right, 3)
        root.addLayout(body)

        self.setCentralWidget(central)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.robots_table.refresh)
        self._timer.timeout.connect(self.events_log.poll)
        self._timer.timeout.connect(self._update_status)
        self._timer.start(1000)
        self._update_status()

    def _load_battle(self):
        path, _ = QFileDialog.getOpenFileName(self, "Charger fichier .battle", "", "Battle files (*.battle)")
        if not path:
            return
        try:
            mvs, rules = parse_battle_file(path)
            battle_config.load(mvs, rules, path)
            self.events_log.append_message(f">>> Fichier charge : {path} (MVS={mvs})")
            self._update_status()
        except Exception as e:
            self.events_log.append_message(f">>> ERREUR chargement : {e}")

    def _update_status(self):
        active = sum(1 for r in registry.all() if r["active"])
        loaded = battle_config._loaded_path or "(aucun)"
        self.status_bar.showMessage(f"Battle: {loaded} | MVS: {battle_config.mvs} | Robots actifs: {active}")
