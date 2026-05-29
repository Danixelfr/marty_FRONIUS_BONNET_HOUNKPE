import sys
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QLineEdit, QFormLayout
)
from PyQt6.QtGui import QAction

class ApprobotInterface(QMainWindow):

    def __init__(self):
        super().__init__()
        
        # 1. Configuration de base de la fenêtre
        self.setWindowTitle("Interface Approbot - Contrôle")
        self.setMinimumSize(800, 500) # Un peu plus large pour loger les 3 colonnes

        # 2. CRÉATION DE LA BARRE DE MENU
        barre_menu = self.menuBar()
        
        # Menu Fichier
        menu_fichier = barre_menu.addMenu("Fichier")
        
        # Action : Charger chorégraphie
        action_charger = QAction("Charger chorégraphie", self)
        action_charger.triggered.connect(self.charger_choregraphie)
        menu_fichier.addAction(action_charger)
        
        # Action : Quitter
        action_quitter = QAction("Quitter", self)
        action_quitter.triggered.connect(self.close) # .close() ferme la fenêtre proprement
        menu_fichier.addAction(action_quitter)


        # 3. CRÉATION DES 3 PANNEAUX (COLONNES)

        # --- PANNEAU GAUCHE : Connexion Robot ---
        panneau_gauche = QWidget()
        layout_gauche = QVBoxLayout()
        layout_gauche.addWidget(QLabel("### CONNEXION ROBOT ###"))
        
        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("Adresse IP du robot")
        self.button_connexion = QPushButton("Connexion")
        self.button_connexion.clicked.connect(self.connecter_robot)
        
        layout_gauche.addWidget(self.input_ip)
        layout_gauche.addWidget(self.button_connexion)
        layout_gauche.addStretch() # Pousse les éléments vers le haut
        panneau_gauche.setLayout(layout_gauche)


        # --- PANNEAU CENTRAL : Contrôles (Déplacements / Expressions) ---
        panneau_central = QWidget()
        layout_central = QVBoxLayout()
        layout_central.addWidget(QLabel("### CONTRÔLES ###"))
        
        self.button_avancer = QPushButton("Avancer ")
        self.button_reculer = QPushButton("Reculer ")
        self.button_expression = QPushButton("Changer Expression ")
        
        layout_central.addWidget(self.button_avancer)
        layout_central.addWidget(self.button_reculer)
        layout_central.addWidget(self.button_expression)
        layout_central.addStretch()
        panneau_central.setLayout(layout_central)


        # --- PANNEAU DROIT : Infos (Batterie, couleur, score, logs) ---
        panneau_droit = QWidget()
        layout_droit = QVBoxLayout()
        layout_droit.addWidget(QLabel("### INFORMATIONS ###"))
        
        # Utilisation d'un QFormLayout pour aligner "Label : Valeur" proprement
        layout_formulaire = QFormLayout()
        self.label_batterie = QLabel("100 %")
        self.label_couleur = QLabel("Bleu")
        self.label_score = QLabel("0")
        self.label_logs = QLabel("Robot déconnecté.")
        
        layout_formulaire.addRow("Batterie :", self.label_batterie)
        layout_formulaire.addRow("Couleur équipe :", self.label_couleur)
        layout_formulaire.addRow("Score actuel :", self.label_score)
        layout_formulaire.addRow("Statut / Logs :", self.label_logs)
        
        layout_droit.addLayout(layout_formulaire)
        layout_droit.addStretch()
        panneau_droit.setLayout(layout_droit)


        # 4. DISPOSITION DES PANNEAUX DANS LE LAYOUT PRINCIPAL
        # On crée un layout horizontal global pour mettre les 3 panneaux côte à côte
        layout_principal = QHBoxLayout()
        layout_principal.addWidget(panneau_gauche)
        layout_principal.addWidget(panneau_central)
        layout_principal.addWidget(panneau_droit)

        # 5. Application du layout dans le widget central
        widget_central_global = QWidget()
        widget_central_global.setLayout(layout_principal)
        self.setCentralWidget(widget_central_global)


    # --- LES FONCTIONS (MÉTHODES) DE LA FENÊTRE ---
    def charger_choregraphie(self):
        print("Ouverture de la boîte de dialogue pour charger une chorégraphie...")

    def connecter_robot(self):
        ip = self.input_ip.text()
        if ip:
            print(f"Tentative de connexion à {ip}...")
            self.label_logs.setText(f"Connexion à {ip} en cours...")
        else:
            print("Veuillez entrer une adresse IP.")