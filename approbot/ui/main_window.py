from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QLineEdit, QFormLayout, QTextEdit,
    QListWidget, QListWidgetItem, QSizePolicy, QFileDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from network.server_client import ServerClient
from network.robot_client import RobotClient
from network.robot_discovery import RobotDiscovery
from dance_parser import parse_dance_file, DanceProgram, DanceParseError
from executeur_choregraphie import ExecuteurChoregraphie


# ── Thread de découverte réseau ────────────────────────────────────────────────

class ThreadRecherche(QThread):
    """Lance la découverte des robots Marty en arrière-plan."""
    robots_trouves = pyqtSignal(list)   # émet list[str] quand c'est fini

    def run(self):
        discovery = RobotDiscovery()
        résultats = discovery.chercher()
        self.robots_trouves.emit(résultats)


# ── Fenêtre principale ─────────────────────────────────────────────────────────

class ApprobotInterface(QMainWindow):

    def __init__(self):
        super().__init__()

        self.client_serveur: ServerClient | None = None
        self.client_robot: RobotClient = RobotClient()
        self._thread_recherche: ThreadRecherche | None = None
        self.choregraphie: DanceProgram | None = None
        self._executeur: ExecuteurChoregraphie | None = None

        self.setWindowTitle("Interface Approbot - Contrôle")
        self.setMinimumSize(1100, 650)

        # ── BARRE DE MENU ──────────────────────────────────────────────
        barre_menu = self.menuBar()
        menu_fichier = barre_menu.addMenu("Fichier")

        action_charger = QAction("Charger chorégraphie", self)
        action_charger.triggered.connect(self.charger_choregraphie)
        menu_fichier.addAction(action_charger)

        action_quitter = QAction("Quitter", self)
        action_quitter.triggered.connect(self.close)
        menu_fichier.addAction(action_quitter)

        # ── COLONNE GAUCHE ─────────────────────────────────────────────
        # Divisée en deux sous-sections : serveur + robot
        colonne_gauche = QWidget()
        layout_colonne_gauche = QVBoxLayout()
        layout_colonne_gauche.setSpacing(16)

        # -- Section connexion SERVEUR --
        layout_colonne_gauche.addWidget(self._separateur("CONNEXION SERVEUR"))

        self.input_ip_serveur = QLineEdit()
        self.input_ip_serveur.setPlaceholderText("IP serveur (ex: 192.168.1.42:8080)")

        self.btn_connecter_serveur = QPushButton("Connexion  (POST /hello)")
        self.btn_connecter_serveur.clicked.connect(self.connecter_serveur)

        self.btn_deconnecter_serveur = QPushButton("Déconnexion  (POST /bye)")
        self.btn_deconnecter_serveur.clicked.connect(self.deconnecter_serveur)
        self.btn_deconnecter_serveur.setEnabled(False)

        layout_colonne_gauche.addWidget(self.input_ip_serveur)
        layout_colonne_gauche.addWidget(self.btn_connecter_serveur)
        layout_colonne_gauche.addWidget(self.btn_deconnecter_serveur)

        # -- Section connexion ROBOT --
        layout_colonne_gauche.addWidget(self._separateur("CONNEXION ROBOT"))

        self.input_ip_robot = QLineEdit()
        self.input_ip_robot.setPlaceholderText("IP robot (ex: 192.168.1.10)")

        self.btn_connecter_robot = QPushButton("Connecter au robot")
        self.btn_connecter_robot.clicked.connect(self.connecter_robot)

        self.btn_deconnecter_robot = QPushButton("Déconnecter le robot")
        self.btn_deconnecter_robot.clicked.connect(self.deconnecter_robot)
        self.btn_deconnecter_robot.setEnabled(False)

        self.btn_recherche_auto = QPushButton("🔍  Recherche automatique")
        self.btn_recherche_auto.clicked.connect(self.lancer_recherche_auto)

        # Liste des robots trouvés lors de la recherche auto
        self.liste_robots = QListWidget()
        self.liste_robots.setMaximumHeight(100)
        self.liste_robots.setVisible(False)
        self.liste_robots.itemDoubleClicked.connect(self.selectionner_robot)

        layout_colonne_gauche.addWidget(self.input_ip_robot)
        layout_colonne_gauche.addWidget(self.btn_connecter_robot)
        layout_colonne_gauche.addWidget(self.btn_deconnecter_robot)
        layout_colonne_gauche.addWidget(self.btn_recherche_auto)
        layout_colonne_gauche.addWidget(self.liste_robots)
        layout_colonne_gauche.addStretch()

        colonne_gauche.setLayout(layout_colonne_gauche)

        # ── COLONNE CENTRALE : Contrôles robot + Tests API ────────────
        colonne_centrale = QWidget()
        layout_central = QVBoxLayout()
        layout_central.setSpacing(6)

        # -- Déplacements --
        layout_central.addWidget(self._separateur("DÉPLACEMENTS"))
        self.btn_avancer      = QPushButton("⬆  Avancer (U)")
        self.btn_reculer      = QPushButton("⬇  Reculer (B)")
        self.btn_gauche       = QPushButton("⬅  Gauche (L)")
        self.btn_droite       = QPushButton("➡  Droite (R)")
        for btn in (self.btn_avancer, self.btn_reculer,
                    self.btn_gauche, self.btn_droite):
            btn.setEnabled(False)
            layout_central.addWidget(btn)
        self.btn_avancer.clicked.connect(lambda: self._cmd_robot(self.client_robot.avancer))
        self.btn_reculer.clicked.connect(lambda: self._cmd_robot(self.client_robot.reculer))
        self.btn_gauche.clicked.connect(lambda: self._cmd_robot(self.client_robot.aller_gauche))
        self.btn_droite.clicked.connect(lambda: self._cmd_robot(self.client_robot.aller_droite))

        # -- Bras --
        layout_central.addWidget(self._separateur("BRAS"))
        self.btn_alu = QPushButton("ALU — Bras G haut")
        self.btn_aru = QPushButton("ARU — Bras D haut")
        self.btn_alb = QPushButton("ALB — Bras G arrière")
        self.btn_arb = QPushButton("ARB — Bras D arrière")
        self.btn_bras_neutres = QPushButton("Bras neutres")
        for btn in (self.btn_alu, self.btn_aru, self.btn_alb,
                    self.btn_arb, self.btn_bras_neutres):
            btn.setEnabled(False)
            layout_central.addWidget(btn)
        self.btn_alu.clicked.connect(lambda: self._cmd_robot(self.client_robot.lever_bras_gauche))
        self.btn_aru.clicked.connect(lambda: self._cmd_robot(self.client_robot.lever_bras_droit))
        self.btn_alb.clicked.connect(lambda: self._cmd_robot(self.client_robot.bras_gauche_arriere))
        self.btn_arb.clicked.connect(lambda: self._cmd_robot(self.client_robot.bras_droit_arriere))
        self.btn_bras_neutres.clicked.connect(lambda: self._cmd_robot(self.client_robot.bras_neutres))

        # -- Expressions --
        layout_central.addWidget(self._separateur("EXPRESSIONS"))
        self.btn_xnt = QPushButton("XNT — Neutre")
        self.btn_xsd = QPushButton("XSD — Triste 😢")
        self.btn_xng = QPushButton("XNG — Colère 😠")
        self.btn_xhp = QPushButton("XHP — Content 😊")
        self.btn_xdn = QPushButton("XDN — Enjoué 🤩")
        for btn in (self.btn_xnt, self.btn_xsd, self.btn_xng,
                    self.btn_xhp, self.btn_xdn):
            btn.setEnabled(False)
            layout_central.addWidget(btn)
        self.btn_xnt.clicked.connect(lambda: self._cmd_robot(self.client_robot.expression_neutre))
        self.btn_xsd.clicked.connect(lambda: self._cmd_robot(self.client_robot.expression_triste))
        self.btn_xng.clicked.connect(lambda: self._cmd_robot(self.client_robot.expression_colere))
        self.btn_xhp.clicked.connect(lambda: self._cmd_robot(self.client_robot.expression_content))
        self.btn_xdn.clicked.connect(lambda: self._cmd_robot(self.client_robot.expression_enjoue))

        # -- Tests API serveur --
        layout_central.addWidget(self._separateur("TESTS API SERVEUR"))
        self.button_ping  = QPushButton("GET  /  (ping)")
        self.button_start = QPushButton("POST /start")
        self.button_score = QPushButton("GET  /score")
        self.button_ping.clicked.connect(self.tester_ping)
        self.button_start.clicked.connect(self.tester_start)
        self.button_score.clicked.connect(self.tester_score)
        for btn in (self.button_ping, self.button_start, self.button_score):
            btn.setEnabled(False)
            layout_central.addWidget(btn)

        # POST /step — champs + bouton
        self.input_step_col = QLineEdit()
        self.input_step_col.setPlaceholderText("col (ex: G)")
        self.input_step_arm = QLineEdit()
        self.input_step_arm.setPlaceholderText("arm (ex: ALU+ARU)")
        self.input_step_exp = QLineEdit()
        self.input_step_exp.setPlaceholderText("exp (ex: XNT)")
        self.button_step = QPushButton("POST /step")
        self.button_step.setEnabled(False)
        self.button_step.clicked.connect(self.tester_step)
        for w in (self.input_step_col, self.input_step_arm,
                  self.input_step_exp, self.button_step):
            layout_central.addWidget(w)

        layout_central.addStretch()
        colonne_centrale.setLayout(layout_central)

        # ── COLONNE DROITE : Infos + Logs ─────────────────────────────
        colonne_droite = QWidget()
        layout_droit = QVBoxLayout()
        layout_droit.addWidget(self._separateur("INFORMATIONS"))

        layout_formulaire = QFormLayout()
        self.label_batterie     = QLabel("- %")
        self.label_couleur      = QLabel("-")
        self.label_score        = QLabel("0")
        self.label_rid          = QLabel("-")
        self.label_statut_robot = QLabel("Non connecté")
        self.label_statut_serveur = QLabel("Non connecté")

        layout_formulaire.addRow("Batterie :",          self.label_batterie)
        layout_formulaire.addRow("Couleur équipe :",    self.label_couleur)
        layout_formulaire.addRow("Score actuel :",      self.label_score)
        layout_formulaire.addRow("RID serveur :",       self.label_rid)
        layout_formulaire.addRow("Statut robot :",      self.label_statut_robot)
        layout_formulaire.addRow("Statut serveur :",    self.label_statut_serveur)
        layout_droit.addLayout(layout_formulaire)

        # -- Chorégraphie chargée --
        layout_droit.addWidget(self._separateur("CHORÉGRAPHIE"))
        self.label_fichier_dance = QLabel("Aucun fichier chargé.")
        self.label_fichier_dance.setWordWrap(True)
        layout_droit.addWidget(self.label_fichier_dance)

        self.zone_choregraphie = QTextEdit()
        self.zone_choregraphie.setReadOnly(True)
        self.zone_choregraphie.setMaximumHeight(180)
        self.zone_choregraphie.setPlaceholderText(
            "Les mouvements et règles apparaîtront ici après chargement."
        )
        layout_droit.addWidget(self.zone_choregraphie)

        layout_droit.addWidget(self._separateur("LOGS"))
        self.zone_logs = QTextEdit()
        self.zone_logs.setReadOnly(True)
        layout_droit.addWidget(self.zone_logs)

        btn_effacer = QPushButton("Effacer les logs")
        btn_effacer.clicked.connect(self.zone_logs.clear)
        layout_droit.addWidget(btn_effacer)

        colonne_droite.setLayout(layout_droit)

        # ── LAYOUT PRINCIPAL ───────────────────────────────────────────
        layout_principal = QHBoxLayout()
        layout_principal.addWidget(colonne_gauche,   stretch=2)
        layout_principal.addWidget(colonne_centrale, stretch=1)
        layout_principal.addWidget(colonne_droite,   stretch=3)

        widget_central = QWidget()
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

        self.log("Application démarrée.")

    # ── UTILITAIRES UI ─────────────────────────────────────────────────

    def _separateur(self, titre: str) -> QLabel:
        """Label stylisé utilisé comme séparateur de section."""
        label = QLabel(f"── {titre} ──")
        label.setStyleSheet("font-weight: bold; color: #555;")
        return label

    def log(self, message: str, niveau: str = "INFO"):
        horodatage = datetime.now().strftime("%H:%M:%S")
        couleurs = {"INFO": "black", "OK": "green", "ERREUR": "red", "WARN": "orange"}
        couleur = couleurs.get(niveau, "black")
        self.zone_logs.append(
            f'<span style="color:gray">[{horodatage}]</span> '
            f'<span style="color:{couleur}"><b>[{niveau}]</b> {message}</span>'
        )

    # ── CONNEXION SERVEUR ──────────────────────────────────────────────

    def connecter_serveur(self):
        ip = self.input_ip_serveur.text().strip()
        if not ip:
            self.log("Veuillez entrer l'adresse IP du serveur.", "WARN")
            return
        self.log(f"Envoi POST /hello → {ip} …")
        try:
            self.client_serveur = ServerClient(ip)
            rid = self.client_serveur.hello()
            self.label_rid.setText(rid)
            self.label_statut_serveur.setText("Connecté")
            self.log(f"Connexion serveur réussie ! RID : {rid}", "OK")
            self.btn_connecter_serveur.setEnabled(False)
            self.btn_deconnecter_serveur.setEnabled(True)
            for btn in (self.button_ping, self.button_start,
                        self.button_score, self.button_step):
                btn.setEnabled(True)
        except Exception as e:
            self.client_serveur = None
            self.log(f"Échec POST /hello : {e}", "ERREUR")

    def deconnecter_serveur(self):
        if self.client_serveur is None:
            return
        self.log("Envoi POST /bye …")
        try:
            self.client_serveur.bye()
            self.log("Déconnexion serveur OK.", "OK")
        except Exception as e:
            self.log(f"Échec POST /bye : {e}", "ERREUR")
        finally:
            self.client_serveur = None
            self.label_rid.setText("-")
            self.label_statut_serveur.setText("Non connecté")
            self.btn_connecter_serveur.setEnabled(True)
            self.btn_deconnecter_serveur.setEnabled(False)
            for btn in (self.button_ping, self.button_start,
                        self.button_score, self.button_step):
                btn.setEnabled(False)

    # ── CONNEXION ROBOT ────────────────────────────────────────────────

    def connecter_robot(self):
        ip = self.input_ip_robot.text().strip()
        if not ip:
            self.log("Veuillez entrer l'adresse IP du robot.", "WARN")
            return
        self.log(f"Connexion au robot Marty → {ip} …")
        try:
            self.client_robot.connect(ip)
            self.label_statut_robot.setText(f"Connecté ({ip})")
            self.log(f"Robot connecté sur {ip}", "OK")
            self.btn_connecter_robot.setEnabled(False)
            self.btn_deconnecter_robot.setEnabled(True)
            self.btn_recherche_auto.setEnabled(False)
            self._set_boutons_robot(True)
        except Exception as e:
            self.log(f"Échec connexion robot : {e}", "ERREUR")

    def deconnecter_robot(self):
        self.log("Déconnexion du robot …")
        try:
            self.client_robot.disconnect()
            self.label_statut_robot.setText("Non connecté")
            self.log("Robot déconnecté.", "OK")
        except Exception as e:
            self.log(f"Erreur déconnexion robot : {e}", "ERREUR")
        finally:
            self.btn_connecter_robot.setEnabled(True)
            self.btn_deconnecter_robot.setEnabled(False)
            self.btn_recherche_auto.setEnabled(True)
            self._set_boutons_robot(False)

    def _set_boutons_robot(self, actif: bool) -> None:
        """Active ou désactive tous les boutons de contrôle robot."""
        for btn in (self.btn_avancer, self.btn_reculer,
                    self.btn_gauche, self.btn_droite,
                    self.btn_alu, self.btn_aru, self.btn_alb,
                    self.btn_arb, self.btn_bras_neutres,
                    self.btn_xnt, self.btn_xsd, self.btn_xng,
                    self.btn_xhp, self.btn_xdn):
            btn.setEnabled(actif)

    def _cmd_robot(self, methode) -> None:
        """Exécute une commande robot et logue le résultat."""
        try:
            methode()
            self.log(f"Commande exécutée : {methode.__name__}", "OK")
        except Exception as e:
            self.log(f"Erreur commande robot : {e}", "ERREUR")

    # ── RECHERCHE AUTOMATIQUE ──────────────────────────────────────────

    def lancer_recherche_auto(self):
        """Démarre la recherche réseau dans un thread séparé."""
        self.log("Recherche automatique des robots Marty sur le réseau …")
        self.btn_recherche_auto.setEnabled(False)
        self.btn_recherche_auto.setText("Recherche en cours …")
        self.liste_robots.clear()
        self.liste_robots.setVisible(False)

        self._thread_recherche = ThreadRecherche()
        self._thread_recherche.robots_trouves.connect(self._on_robots_trouves)
        self._thread_recherche.start()

    def _on_robots_trouves(self, robots: list):
        """Callback appelé quand la recherche se termine."""
        self.btn_recherche_auto.setEnabled(True)
        self.btn_recherche_auto.setText("🔍  Recherche automatique")

        if not robots:
            self.log("Aucun robot Marty trouvé sur le réseau.", "WARN")
            return

        self.log(f"{len(robots)} robot(s) trouvé(s) : {', '.join(robots)}", "OK")
        self.liste_robots.clear()
        for ip in robots:
            self.liste_robots.addItem(QListWidgetItem(ip))
        self.liste_robots.setVisible(True)

    def selectionner_robot(self, item: QListWidgetItem):
        """Double-clic sur un robot trouvé → remplit le champ IP et connecte."""
        ip = item.text()
        self.input_ip_robot.setText(ip)
        self.connecter_robot()

    # ── TESTS API SERVEUR ──────────────────────────────────────────────

    def tester_ping(self):
        self.log("Envoi GET / …")
        try:
            version = self.client_serveur.ping()
            self.log(f"Serveur répond — version : {version}", "OK")
        except Exception as e:
            self.log(f"Échec GET / : {e}", "ERREUR")

    def tester_start(self):
        self.log("Envoi POST /start …")
        try:
            nb_pas = self.client_serveur.start()
            self.log(f"Chorégraphie démarrée — nombre de pas : {nb_pas}", "OK")
        except Exception as e:
            self.log(f"Échec POST /start : {e}", "ERREUR")
            return

        # Si une chorégraphie est chargée et le robot connecté, on l'exécute
        if self.choregraphie is None:
            self.log("Aucune chorégraphie chargée (Fichier > Charger chorégraphie).", "WARN")
            return
        if not self.client_robot.is_connected:
            self.log("Robot non connecté : impossible d'exécuter la chorégraphie.", "WARN")
            return
        if self._executeur is not None and self._executeur.isRunning():
            self.log("Une chorégraphie est déjà en cours d'exécution.", "WARN")
            return

        self._lancer_execution_choregraphie(nb_pas)

    def _lancer_execution_choregraphie(self, nb_pas: int) -> None:
        """Démarre l'exécution de la chorégraphie chargée dans un thread dédié."""
        self.log(f"Lancement de la chorégraphie ({nb_pas} pas) …")
        self._set_boutons_execution(False)

        self._executeur = ExecuteurChoregraphie(
            self.client_robot, self.client_serveur, self.choregraphie, nb_pas
        )
        self._executeur.log.connect(self.log)
        self._executeur.score_maj.connect(lambda pts: self.label_score.setText(str(pts)))
        self._executeur.termine.connect(self._on_choregraphie_terminee)
        self._executeur.start()

    def _on_choregraphie_terminee(self) -> None:
        self._set_boutons_execution(True)

    def _set_boutons_execution(self, actif: bool) -> None:
        """Active/désactive les contrôles pendant l'exécution automatique de la chorégraphie."""
        self._set_boutons_robot(actif)
        for btn in (self.button_ping, self.button_start,
                    self.button_score, self.button_step):
            btn.setEnabled(actif)

    def tester_score(self):
        self.log("Envoi GET /score …")
        try:
            points = self.client_serveur.score()
            self.label_score.setText(str(points))
            self.log(f"Score reçu : {points} points", "OK")
        except Exception as e:
            self.log(f"Échec GET /score : {e}", "ERREUR")

    def tester_step(self):
        col = self.input_step_col.text().strip()
        arm = self.input_step_arm.text().strip()
        exp = self.input_step_exp.text().strip()
        if not col or not arm or not exp:
            self.log("Remplissez col, arm et exp avant d'envoyer /step.", "WARN")
            return
        self.log(f"Envoi POST /step (col={col}, arm={arm}, exp={exp}) …")
        try:
            points = self.client_serveur.step(col, arm, exp)
            self.label_score.setText(str(points))
            self.log(f"/step OK — points obtenus : {points}", "OK")
        except Exception as e:
            self.log(f"Échec POST /step : {e}", "ERREUR")

    # ── DIVERS ─────────────────────────────────────────────────────────

    def charger_choregraphie(self):
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Charger une chorégraphie", "", "Fichiers dance (*.dance);;Tous (*)"
        )
        if not chemin:
            return
        try:
            self.choregraphie = parse_dance_file(chemin)
            nom = chemin.split("/")[-1].split("\\")[-1]
            self.label_fichier_dance.setText(f"📄 {nom}")
            self.zone_choregraphie.setPlainText(repr(self.choregraphie))
            self.log(f"Chorégraphie chargée : {nom} "
                     f"({len(self.choregraphie.movements)} mouvements, "
                     f"{len(self.choregraphie.act_rules)} règles ACT)", "OK")
        except DanceParseError as e:
            self.log(f"Fichier .dance invalide : {e}", "ERREUR")
        except Exception as e:
            self.log(f"Erreur chargement .dance : {e}", "ERREUR")

    def rafraichir_score(self):
        self.tester_score()
