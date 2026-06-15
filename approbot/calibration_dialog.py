"""
Dialogue de calibration des couleurs du capteur de Marty — D-006.

Permet d'associer les valeurs RGB réellement mesurées par le capteur de
couleur du robot aux codes couleur standard du jeu (N, P, B, Y, C, G, R).
Pour chaque couleur, l'utilisateur pose le robot sur la plaque
correspondante puis clique sur « Capturer » : la valeur RGB lue par le
capteur est enregistrée pour cette couleur. La calibration peut ensuite
être sauvegardée pour être réutilisée par `RobotClient.lire_couleur()`.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QMessageBox,
)

from calibration_couleurs import CODES_COULEURS, COULEURS_PAR_DEFAUT, sauvegarder_calibration


class CalibrationCouleursDialog(QDialog):
    """Fenêtre de calibration des couleurs de plaque détectées par le robot."""

    def __init__(self, client_robot, parent=None):
        super().__init__(parent)
        self.client_robot = client_robot

        # True si la calibration a été enregistrée pendant cette session.
        self.modifie = False

        # Valeurs RGB capturées, initialisées avec la calibration actuelle
        # (chargée depuis le fichier, ou valeurs par défaut).
        self.valeurs: dict[str, tuple[int, int, int]] = dict(client_robot.calibration)

        self.setWindowTitle("Calibration des couleurs")
        self.setMinimumWidth(440)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(
            "Posez le robot sur chaque plaque de couleur, puis cliquez sur "
            "« Capturer » pour enregistrer la valeur RGB lue par le capteur."
        ))

        grille = QGridLayout()
        grille.addWidget(QLabel("<b>Couleur</b>"), 0, 0)
        grille.addWidget(QLabel("<b>Valeur RGB</b>"), 0, 1)
        grille.addWidget(QLabel("<b>Aperçu</b>"), 0, 2)

        self._labels_valeur: dict[str, QLabel] = {}
        self._labels_apercu: dict[str, QLabel] = {}

        for i, (code, nom) in enumerate(CODES_COULEURS.items(), start=1):
            grille.addWidget(QLabel(f"{nom} ({code})"), i, 0)

            label_valeur = QLabel(self._texte_rgb(self.valeurs[code]))
            self._labels_valeur[code] = label_valeur
            grille.addWidget(label_valeur, i, 1)

            label_apercu = QLabel()
            label_apercu.setFixedSize(28, 20)
            self._labels_apercu[code] = label_apercu
            grille.addWidget(label_apercu, i, 2)
            self._maj_apercu(code)

            btn_capturer = QPushButton("Capturer")
            btn_capturer.clicked.connect(lambda _checked, c=code: self._capturer(c))
            grille.addWidget(btn_capturer, i, 3)

        layout.addLayout(grille)

        # -- Boutons bas de fenêtre --
        layout_bas = QHBoxLayout()

        btn_reinitialiser = QPushButton("Valeurs par défaut")
        btn_reinitialiser.clicked.connect(self._reinitialiser)

        btn_enregistrer = QPushButton("Enregistrer")
        btn_enregistrer.clicked.connect(self._enregistrer)

        btn_fermer = QPushButton("Fermer")
        btn_fermer.clicked.connect(self.reject)

        layout_bas.addWidget(btn_reinitialiser)
        layout_bas.addStretch()
        layout_bas.addWidget(btn_enregistrer)
        layout_bas.addWidget(btn_fermer)
        layout.addLayout(layout_bas)

        self.setLayout(layout)

    # ------------------------------------------------------------------

    def _texte_rgb(self, rgb: tuple[int, int, int]) -> str:
        return f"R={rgb[0]:3d}  G={rgb[1]:3d}  B={rgb[2]:3d}"

    def _maj_apercu(self, code: str) -> None:
        r, g, b = self.valeurs[code]
        self._labels_apercu[code].setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); border: 1px solid #888;"
        )

    def _capturer(self, code: str) -> None:
        """Lit la couleur brute actuellement détectée et l'associe à `code`."""
        rgb = self.client_robot.lire_couleur_brute()
        if rgb is None:
            QMessageBox.warning(
                self, "Capture impossible",
                "Impossible de lire la couleur depuis le capteur du robot.\n"
                "Vérifiez que le robot est bien connecté.",
            )
            return

        self.valeurs[code] = rgb
        self._labels_valeur[code].setText(self._texte_rgb(rgb))
        self._maj_apercu(code)

    def _reinitialiser(self) -> None:
        """Réinitialise toutes les valeurs aux références par défaut (non sauvegardé)."""
        self.valeurs = dict(COULEURS_PAR_DEFAUT)
        for code in CODES_COULEURS:
            self._labels_valeur[code].setText(self._texte_rgb(self.valeurs[code]))
            self._maj_apercu(code)

    def _enregistrer(self) -> None:
        """Sauvegarde la calibration courante et la recharge dans le client robot."""
        sauvegarder_calibration(self.valeurs)
        self.client_robot.recharger_calibration()
        self.modifie = True
        QMessageBox.information(
            self, "Calibration enregistrée",
            "La calibration des couleurs a été enregistrée et sera utilisée "
            "pour la détection de couleur.",
        )
