import sys
import os
from PyQt6.QtWidgets import QApplication

# dance_parser.py vit dans appserver/ (fichier partagé, pas de copie ici) :
# on ajoute ce dossier au chemin de recherche des modules.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "appserver"))

# On importe la classe depuis le fichier main_window situé dans le dossier ui
from ui.main_window import ApprobotInterface

def main():
    # Lancement de l'application
    app = QApplication(sys.argv)

    # On crée une instance de notre classe importée
    window = ApprobotInterface()
    window.show()

    # On lance la boucle d'exécution
    sys.exit(app.exec())

if __name__ == "__main__":
    main()