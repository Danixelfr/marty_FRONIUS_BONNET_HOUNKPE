import requests
import time


SERVER_URL = ""  
DANCE_FILE = "routine.dance"

class ChoreographyEngine:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.max_moves = 0
        self.dance_moves = []

    def load_dance(self, filepath):
        """Lit les mouvements depuis le fichier .dance"""
        try:
            with open(filepath, 'r') as f:
         
                self.dance_moves = [line.strip() for line in f if line.strip()]
            print(f" {len(self.dance_moves)} mouvements chargés depuis {filepath}")
        except FileNotFoundError:
            print(" Erreur : Fichier .dance introuvable.")
            exit(1)

    def get_act_expression(self, color):
        """Logique ACT : Associe une couleur à une expression"""
        rules = {
            "red": "angry",
            "green": "happy",
            "blue": "surprised",
            "yellow": "excited"
        }
        return rules.get(color.lower(), "neutral")

    def run(self):
        # 1. Appel /start
        print(" Initialisation de la session (/start)...")
        response = self.session.post(f"{self.base_url}/start")
        if response.status_code == 200:
            data = response.json()
            self.max_moves = data.get("max_moves", len(self.dance_moves))
        else:
            print(f" Échec /start: {response.status_code}")
            return

        # 2. Boucle d'exécution
        for i in range(self.max_moves):
            # Gestion de la répétition (Modulo)
            move_to_execute = self.dance_moves[i % len(self.dance_moves)]
            
            print(f"\n[Step {i+1}/{self.max_moves}] Exécution : {move_to_execute}")

            # --- Action Robot ---
            # Exécution du mouvement (bloquant)
            # robot.execute_arm_move(move_to_execute) 
            
            # Perception
            detected_color = "green" # robot.sense_color() 
            expression = self.get_act_expression(detected_color)

            # Application de l'expression
            # robot.set_face(expression)
            print(f" Couleur: {detected_color} -> Expression: {expression}")

            # 3. Envoi /step au serveur
            payload = {
                "step": i,
                "col": detected_color,
                "arm": move_to_execute,
                "exp": expression
            }
            res_step = self.session.post(f"{self.base_url}/step", json=payload)
            if res_step.status_code != 200:
                print(f" Erreur lors de l'envoi du step: {res_step.text}")

            # 4. Reset : Expression neutre + bras repos
            print(" Reset (neutral + rest)...")
            # robot.set_face("neutral")
            # robot.move_arms_to_rest()
            time.sleep(0.5) # Petite pause de sécurité

        # 5. Appel /bye
        print("\n Chorégraphie terminée (/bye)...")
        self.session.post(f"{self.base_url}/bye")

if __name__ == "__main__":
    engine = ChoreographyEngine(SERVER_URL)
    engine.load_dance(DANCE_FILE)
    engine.run()