import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QLineEdit, QFormLayout, QTextEdit
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from network.server_client import ServerClient


class ApprobotInterface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.client: ServerClient | None = None

        self.setWindowTitle("Interface Approbot - Contrôle")
        self.setMinimumSize(1000, 600)

        #  BARRE DE MENU 
        barre_menu = self.menuBar()
        menu_fichier = barre_menu.addMenu("Fichier")

        action_charger = QAction("Charger chorégraphie", self)
        action_charger.triggered.connect(self.charger_choregraphie)
        menu_fichier.addAction(action_charger)

        action_quitter = QAction("Quitter", self)
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)

        #  PANNEAU GAUCHE : Connexion serveur 
        panneau_gauche = QWidget()
        layout_gauche = QVBoxLayout()
        layout_gauche.addWidget(QLabel("### CONNEXION SERVEUR ###"))

        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("IP serveur (ex: 192.168.1.42:8080)")

        self.button_connexion = QPushButton("Connexion  (POST /hello)")
        self.button_connexion.clicked.connect(self.connecter_serveur)

        self.button_deconnexion = QPushButton("Déconnexion  (POST /bye)")
        self.button_deconnexion.clicked.connect(self.deconnecter_serveur)
        self.button_deconnexion.setEnabled(False)

        layout_gauche.addWidget(self.input_ip)
        layout_gauche.addWidget(self.button_connexion)
        layout_gauche.addWidget(self.button_deconnexion)
        layout_gauche.addStretch()
        panneau_gauche.setLayout(layout_gauche)

        #  PANNEAU CENTRAL : Tests API 
        panneau_central = QWidget()
        layout_central = QVBoxLayout()
        layout_central.addWidget(QLabel("### TESTS API SERVEUR ###"))

        self.button_ping   = QPushButton("GET  /  (ping)")
        self.button_start  = QPushButton("POST /start")
        self.button_score  = QPushButton("GET  /score")

        self.button_ping.clicked.connect(self.tester_ping)
        self.button_start.clicked.connect(self.tester_start)
        self.button_score.clicked.connect(self.tester_score)

        for btn in (self.button_ping, self.button_start, self.button_score):
            btn.setEnabled(False)
            layout_central.addWidget(btn)

        layout_central.addStretch()
        panneau_central.setLayout(layout_central)

        #  PANNEAU DROIT : Infos + Logs 
        panneau_droit = QWidget()
        layout_droit = QVBoxLayout()
        layout_droit.addWidget(QLabel("### INFORMATIONS ###"))

        layout_formulaire = QFormLayout()
        self.label_batterie = QLabel("- %")
        self.label_couleur  = QLabel("-")
        self.label_score    = QLabel("0")
        self.label_rid      = QLabel("-")

        layout_formulaire.addRow("Batterie :",        self.label_batterie)
        layout_formulaire.addRow("Couleur équipe :",  self.label_couleur)
        layout_formulaire.addRow("Score actuel :",    self.label_score)
        layout_formulaire.addRow("Identifiant (RID):", self.label_rid)
        layout_droit.addLayout(layout_formulaire)

        # Zone de logs
        layout_droit.addWidget(QLabel("### LOGS ###"))
        self.zone_logs = QTextEdit()
        self.zone_logs.setReadOnly(True)
        self.zone_logs.setMinimumHeight(200)
        layout_droit.addWidget(self.zone_logs)

        btn_effacer = QPushButton("Effacer les logs")
        btn_effacer.clicked.connect(self.zone_logs.clear)
        layout_droit.addWidget(btn_effacer)

        panneau_droit.setLayout(layout_droit)

        #  LAYOUT PRINCIPAL 
        layout_principal = QHBoxLayout()
        layout_principal.addWidget(panneau_gauche, stretch=1)
        layout_principal.addWidget(panneau_central, stretch=1)
        layout_principal.addWidget(panneau_droit, stretch=2)

        widget_central = QWidget()
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

        self.log("Application démarrée.")

    #  LOGS 

    def log(self, message: str, niveau: str = "INFO"):
        horodatage = datetime.now().strftime("%H:%M:%S")
        couleurs = {"INFO": "black", "OK": "green", "ERREUR": "red", "WARN": "orange"}
        couleur = couleurs.get(niveau, "black")
        self.zone_logs.append(
            f'<span style="color:gray">[{horodatage}]</span> '
            f'<span style="color:{couleur}"><b>[{niveau}]</b> {message}</span>'
        )

    #  CONNEXION SERVEUR 

    def connecter_serveur(self):
        """POST /hello → enregistre le robot, récupère le rid."""
        ip = self.input_ip.text().strip()
        if not ip:
            self.log("Veuillez entrer une adresse IP.", "WARN")
            return

        self.log(f"Envoi POST /hello → {ip} …")
        try:
            self.client = ServerClient(ip)
            rid = self.client.hello()
            self.label_rid.setText(rid)
            self.log(f"Connexion réussie ! RID reçu : {rid}", "OK")
            self.button_connexion.setEnabled(False)
            self.button_deconnexion.setEnabled(True)
            for btn in (self.button_ping, self.button_start, self.button_score):
                btn.setEnabled(True)
        except Exception as e:
            self.client = None
            self.log(f"Échec POST /hello : {e}", "ERREUR")

    def deconnecter_serveur(self):
        """POST /bye → déconnecte le robot du serveur."""
        if self.client is None:
            return
        self.log("Envoi POST /bye …")
        try:
            self.client.bye()
            self.log("Déconnexion OK.", "OK")
        except Exception as e:
            self.log(f"Échec POST /bye : {e}", "ERREUR")
        finally:
            self.client = None
            self.label_rid.setText("-")
            self.button_connexion.setEnabled(True)
            self.button_deconnexion.setEnabled(False)
            for btn in (self.button_ping, self.button_start, self.button_score):
                btn.setEnabled(False)

    #  TESTS API 

    def tester_ping(self):
        """GET / → vérifie que le serveur répond."""
        self.log("Envoi GET / …")
        try:
            version = self.client.ping()
            self.log(f"Serveur répond — version : {version}", "OK")
        except Exception as e:
            self.log(f"Échec GET / : {e}", "ERREUR")

    def tester_start(self):
        """POST /start → démarre une chorégraphie."""
        self.log("Envoi POST /start …")
        try:
            nb_pas = self.client.start()
            self.log(f"Chorégraphie démarrée — nombre de pas : {nb_pas}", "OK")
        except Exception as e:
            self.log(f"Échec POST /start : {e}", "ERREUR")

    def tester_score(self):
        """GET /score → récupère le score courant."""
        self.log("Envoi GET /score …")
        try:
            points = self.client.score()
            self.label_score.setText(str(points))
            self.log(f"Score reçu : {points} points", "OK")
        except Exception as e:
            self.log(f"Échec GET /score : {e}", "ERREUR")

    #  DIVERS 

    def charger_choregraphie(self):
        self.log("Chargement de chorégraphie — non implémenté.", "WARN")

    def rafraichir_score(self):
        self.tester_score()
