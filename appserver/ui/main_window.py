from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QStatusBar, QLabel, QComboBox,
)
from PyQt6.QtCore import QTimer
from .robots_table import RobotsTable
from .events_log import EventsLog
from server.registry import registry
from server.battle_config import battle_config
from server.battle.parser import parse_battle_file
from server.server_state import server_state, ServerStatus


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dance Battle - Server")
        self.resize(1100, 700)

        self.robots_table = RobotsTable()
        self.events_log = EventsLog()
        self.btn_load_battle = QPushButton("Charger .battle")
        self.btn_load_battle.clicked.connect(self._load_battle)

        self.status_label = QLabel()
        self.combo_status = QComboBox()
        self.combo_status.addItems(["ACTIVE", "READ_ONLY", "DISABLED"])
        self.combo_status.currentTextChanged.connect(self._on_status_changed)

        central = QWidget()
        root = QVBoxLayout(central)

        top = QHBoxLayout()
        top.addWidget(self.btn_load_battle)
        top.addStretch()
        top.addWidget(QLabel("Serveur :"))
        top.addWidget(self.status_label)
        top.addWidget(self.combo_status)
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

        # on rafraichit l'UI toutes les secondes (le serveur tourne dans un autre thread)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.robots_table.refresh)
        self._timer.timeout.connect(self.events_log.poll)
        self._timer.timeout.connect(self._update_status)
        self._timer.start(1000)
        self._update_status()
        self._refresh_status_visual()

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

    def _on_status_changed(self, text):
        server_state.set_status(ServerStatus[text])
        self.events_log.append_message(f">>> Serveur passe en {text}")
        self._refresh_status_visual()

    def _refresh_status_visual(self):
        styles = {
            ServerStatus.ACTIVE: ("● ACTIF", "#10B981"),
            ServerStatus.READ_ONLY: ("● LECTURE SEULE", "#F59E0B"),
            ServerStatus.DISABLED: ("● DESACTIVE", "#EF4444"),
        }
        text, color = styles[server_state.status]
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
