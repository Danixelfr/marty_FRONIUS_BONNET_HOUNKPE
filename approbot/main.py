import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class ApprobotInterface(QMainWindow):

    def dire_bonjour(self):
            print("Bouton cliqué !")

            
    def __init__(self):
        super().__init__()

        
        
        # 1. On configure la fenêtre via 'self' (puisque l'objet est la fenêtre)
        self.setWindowTitle("interface approbot")
        self.setMinimumSize(500, 500)

        # 2. On crée les boutons en tant qu'attributs (self.nom_variable)
        # Comme ça, ils sont sauvegardés dans l'objet et accessibles partout.
        self.button_connexion = QPushButton("connexion")
        self.button_mouvement = QPushButton("controle mouvement")

        # 3. Création du layout
        layout = QVBoxLayout()
        layout.addWidget(self.button_connexion)
        layout.addWidget(self.button_mouvement)

        # 4. Widget central
        centerWidget = QWidget()
        centerWidget.setLayout(layout)
        self.setCentralWidget(centerWidget)

        self.button_connexion.clicked.connect(self.dire_bonjour)

# --- Lancement de l'application ---
app = QApplication(sys.argv)

# On crée une instance de notre classe
window = ApprobotInterface()
window.show()

app.exec()