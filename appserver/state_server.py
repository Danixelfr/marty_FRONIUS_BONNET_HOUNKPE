import threading

class BattleState:
    """
    Gère les données de la battle de manière sécurisée (Thread-safe).
    Stocke les scores, l'historique et la liste des robots.
    """
    def __init__(self):
        # Dictionnaire principal : { "nom_robot": { "score": 0, "steps": [] } }
        self.robots = {}
        # Verrou pour la sécurité entre les threads
        self.lock = threading.Lock()

    def enregistrer_robot(self, nom_robot):
        """Initialise un nouveau robot s'il n'existe pas encore."""
        with self.lock:
            if nom_robot not in self.robots:
                self.robots[nom_robot] = {
                    "score_total": 0,
                    "historique_steps": []
                }
                print(f"Robot '{nom_robot}' enregistré avec succès.")

    def ajouter_step(self, nom_robot, couleur, bras, expression, points_gagnes):
        """
        Met à jour le score et l'historique d'un robot après un mouvement.
        """
        with self.lock:
            if nom_robot in self.robots:
                # Mise à jour du score cumulatif
                self.robots[nom_robot]["score_total"] += points_gagnes
                

                step_data = {
                    "couleur": couleur,
                    "bras": bras,
                    "expression": expression,
                    "points": points_gagnes
                }
                self.robots[nom_robot]["historique_steps"].append(step_data)
                
                print(f"[{nom_robot}] Score : {self.robots[nom_robot]['score_total']} (+{points_gagnes})")
            else:
                print(f"Erreur : Robot '{nom_robot}' inconnu.")

    def obtenir_classement(self):
        """Retourne les scores de tous les robots pour l'affichage."""
        with self.lock:
            return {nom: data["score_total"] for nom, data in self.robots.items()}
        


state= BattleState()

