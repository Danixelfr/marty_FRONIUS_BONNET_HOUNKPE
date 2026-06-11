"""
Exécution automatique d'une chorégraphie .dance sur le robot Marty.

Pour chaque pas de la chorégraphie :
  1. le robot effectue le déplacement
  2. il détecte la couleur de la plaque sous lui
  3. il applique la réaction (bras + expression) définie par la règle ACT
     correspondant à cette couleur
  4. il envoie le pas (couleur, bras, expression) au serveur via POST /step
  5. il revient en position neutre avant le pas suivant

Le nombre de pas effectivement joués est celui renvoyé par POST /start
(la séquence du fichier .dance est répétée ou tronquée pour l'atteindre).
"""

import time
import itertools

from PyQt6.QtCore import QThread, pyqtSignal

from dance_parser import DanceProgram


# Délai (secondes) laissé au robot pour terminer un pas de déplacement.
# À ajuster selon la vitesse réelle du robot.
DUREE_PAR_PAS = 1.6

# Délai (secondes) laissé au robot pour montrer sa réaction (bras + expression)
# avant l'envoi du /step.
DUREE_REACTION = 0.6


class ExecuteurChoregraphie(QThread):
    """Déroule une chorégraphie sur le robot et reporte chaque pas au serveur."""

    log = pyqtSignal(str, str)     # (message, niveau)
    score_maj = pyqtSignal(int)    # score total après le dernier /step
    termine = pyqtSignal()

    # direction (DanceProgram) -> méthode RobotClient
    DEPLACEMENTS = {
        "forward": "avancer",
        "backward": "reculer",
        "left": "aller_gauche",
        "right": "aller_droite",
    }

    # code bras (.dance / .battle) -> méthode RobotClient
    ACTIONS_BRAS = {
        "ALU": "lever_bras_gauche",
        "ARU": "lever_bras_droit",
        "ALB": "bras_gauche_arriere",
        "ARB": "bras_droit_arriere",
    }

    # code expression (.dance / .battle) -> méthode RobotClient
    ACTIONS_EXPRESSION = {
        "XNT": "expression_neutre",
        "XSD": "expression_triste",
        "XNG": "expression_colere",
        "XHP": "expression_content",
        "XDN": "expression_enjoue",
    }

    def __init__(self, client_robot, client_serveur, choregraphie: DanceProgram, nb_pas: int):
        super().__init__()
        self.client_robot = client_robot
        self.client_serveur = client_serveur
        self.choregraphie = choregraphie
        self.nb_pas = nb_pas
        self._stop_demande = False

    def arreter(self):
        """Demande l'arrêt propre de la chorégraphie après le pas en cours."""
        self._stop_demande = True

    def run(self):
        if not self.choregraphie.movements:
            self.log.emit("La chorégraphie ne contient aucun mouvement (section SEQ vide).", "ERREUR")
            self.termine.emit()
            return

        # On boucle/tronque la séquence du fichier .dance pour atteindre
        # exactement nb_pas mouvements (cf. spécification du format .dance).
        mouvements = list(itertools.islice(
            itertools.cycle(self.choregraphie.movements), self.nb_pas
        ))

        # Position de départ : neutre
        self._neutre()

        for i, mouvement in enumerate(mouvements, start=1):
            if self._stop_demande:
                self.log.emit("Chorégraphie interrompue.", "WARN")
                break

            try:
                # 1. Déplacement
                self.log.emit(
                    f"Pas {i}/{self.nb_pas} — déplacement "
                    f"{mouvement.direction} ({mouvement.steps} pas)", "INFO"
                )
                methode_deplacement = getattr(self.client_robot, self.DEPLACEMENTS[mouvement.direction])
                methode_deplacement(mouvement.steps)
                time.sleep(DUREE_PAR_PAS * mouvement.steps)

                # 2. Détection de la couleur sous le robot
                couleur = self.client_robot.lire_couleur()
                self.log.emit(f"Couleur détectée : {couleur}", "INFO")

                # 3. Réaction (bras + expression) selon la règle ACT correspondante
                regle = next(
                    (r for r in self.choregraphie.act_rules if r.color == couleur),
                    None,
                )

                arm = ""
                exp = "XNT"
                if regle is not None:
                    for action in regle.actions:
                        methode_bras = self.ACTIONS_BRAS.get(action)
                        if methode_bras:
                            getattr(self.client_robot, methode_bras)()
                    arm = "+".join(regle.actions)

                    if regle.expression:
                        exp = regle.expression
                        methode_exp = self.ACTIONS_EXPRESSION.get(exp)
                        if methode_exp:
                            getattr(self.client_robot, methode_exp)()

                    time.sleep(DUREE_REACTION)

                # 4. Envoi du pas au serveur/arbitre
                points = self.client_serveur.step(couleur, arm, exp)
                self.log.emit(
                    f"/step → col={couleur}, arm={arm or '-'}, exp={exp} "
                    f"→ +{points} pt(s)", "OK"
                )

                # 5. Score total à jour (GET /score)
                try:
                    self.score_maj.emit(self.client_serveur.score())
                except Exception:
                    pass

            except Exception as e:
                self.log.emit(f"Erreur au pas {i} : {e}", "ERREUR")

            finally:
                # Retour en position neutre avant le pas suivant
                self._neutre()

        self.log.emit("Chorégraphie terminée.", "OK")
        self.termine.emit()

    def _neutre(self):
        try:
            self.client_robot.bras_neutres()
            self.client_robot.expression_neutre()
        except Exception as e:
            self.log.emit(f"Erreur retour position neutre : {e}", "ERREUR")
