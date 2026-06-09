import sys
from PyQt6.QtWidgets import QApplication
# On importe la classe depuis le fichier main_window situé dans le dossier ui
from ui.main_window import ApprobotInterface

def main():
    # --- Lancement de l'application ---
    app = QApplication(sys.argv)

    # On crée une instance de notre classe importée
    window = ApprobotInterface()
    window.show()

    # On lance la boucle d'exécution
    sys.exit(app.exec())

if __name__ == "__main__":
    main()