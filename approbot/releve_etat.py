"""
Relevé périodique de l'état du robot (batterie + couleur de plaque) — D-005.

Tourne dans un thread dédié pour ne pas bloquer l'interface PyQt. Peut être
mis en pause (par exemple pendant l'exécution d'une chorégraphie) afin
d'éviter d'envoyer des commandes au robot en même temps qu'un autre thread
(ExecuteurChoregraphie).
"""

import threading

from PyQt6.QtCore import QThread, pyqtSignal


# Délai (secondes) entre deux relevés batterie/couleur.
INTERVALLE_PAR_DEFAUT = 3.0


class ReleveEtatRobot(QThread):
    """Relève périodiquement la batterie et la couleur de plaque du robot."""

    # (pourcentage de batterie ou None, code couleur ou None)
    etat_maj = pyqtSignal(object, object)

    def __init__(self, client_robot, intervalle: float = INTERVALLE_PAR_DEFAUT):
        super().__init__()
        self.client_robot = client_robot
        self.intervalle = intervalle
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()  # set = relevés en pause

    def run(self) -> None:
        while not self._stop_event.is_set():
            if not self._pause_event.is_set():
                batterie = self._lire_batterie_securisee()
                couleur = self._lire_couleur_securisee()
                self.etat_maj.emit(batterie, couleur)

            # Attente interruptible : réagit immédiatement à arreter()
            self._stop_event.wait(self.intervalle)

    def _lire_batterie_securisee(self):
        try:
            return self.client_robot.lire_batterie()
        except Exception:
            return None

    def _lire_couleur_securisee(self):
        try:
            return self.client_robot.lire_couleur()
        except Exception:
            return None

    def pause(self) -> None:
        """Suspend les relevés (ex : pendant l'exécution d'une chorégraphie)."""
        self._pause_event.set()

    def reprendre(self) -> None:
        """Reprend les relevés après une pause."""
        self._pause_event.clear()

    def arreter(self) -> None:
        """Arrête définitivement le thread de relevé."""
        self._stop_event.set()
