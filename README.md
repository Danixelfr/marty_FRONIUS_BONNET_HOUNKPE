# 🤖 Dance Battle — Marty TP2

> Projet robotique 3A Polytech | Groupe : Fronius · Bonnet · Hounkpe

Deux robots s'affrontent dans une arène colorée : chacun enchaîne une chorégraphie, un arbitre calcule les scores en temps réel.

---

## Structure du projet

```
polytech-3a-robot/
├── approbot/      # Application robot/joueur (PyQt)
├── appserver/     # Application serveur/arbitre (HTTP)
└── README.md
```

---

## Prérequis

- Python 3.8+
- Git

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd polytech-3a-robot
```

### 2. Créer les environnements virtuels

Chaque application dispose de son propre venv.

**Application robot (`approbot`) :**
```bash
cd approbot
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

**Serveur arbitre (`appserver`) :**
```bash
cd appserver
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

---

## Utilisation

### Démarrer le serveur arbitre

```bash
cd appserver
source venv/bin/activate
python app.py
```

Le serveur HTTP démarre et expose l'API REST sur le port configuré. Vérifier qu'il répond :

```bash
curl http://localhost:<port>/
# → {"version": "1.2"}
```

### Lancer l'application robot

```bash
cd approbot
source venv/bin/activate
python main.py
```

L'interface PyQt permet de se connecter à un robot (IP manuelle ou recherche automatique), de charger un fichier `.dance`, et d'envoyer la chorégraphie au serveur.

---

## Fichiers de configuration

| Fichier | Rôle | Utilisé par |
|---------|------|-------------|
| `.dance` | Définit la chorégraphie du robot (mouvements + expressions selon la couleur) | `approbot` |
| `.battle` | Définit les règles de scoring par couleur et mouvement | `appserver` |

### Exemple minimal `.dance`

```
SEQ 1
1U
1L
2B
ACT
N ARU XNG
B XSD
```

### Exemple minimal `.battle`

```
MVS 10
[N]
ALB+ARB=1
XSD=1
[R]
ALU+ARU=2
XNG=3
```

---

## API du serveur (résumé)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET`  | `/`       | Vérifier la disponibilité du serveur |
| `POST` | `/hello`  | Enregistrer un robot → reçoit un `rid` |
| `POST` | `/start`  | Démarrer une chorégraphie → reçoit le nombre de pas |
| `POST` | `/step`   | Envoyer un mouvement → reçoit les points obtenus |
| `GET`  | `/score`  | Consulter le score total d'un robot |
| `POST` | `/bye`    | Déconnecter un robot |

Toutes les requêtes et réponses sont en JSON.

---

## Workflow Git

| Branche | Rôle |
|---------|------|
| `main` | Branche principale protégée — merge via PR uniquement |
| `develop` | Branche d'intégration continue |
| `feature/<nom>-<description>` | Branche de fonctionnalité |

### Démarrer une nouvelle fonctionnalité

```bash
git checkout develop
git pull origin develop
git checkout -b feature/<votre-nom>-<description>
# ex : git checkout -b feature/bonnet-scoring-engine
```

### Soumettre le travail

```bash
git add .
git commit -m "feat: description du changement"
git push origin feature/<votre-nom>-<description>
# → ouvrir une Pull Request vers develop sur GitHub
```

---

## Contributeurs

| Nom | GitHub |
|-----|--------|
| Joseph Hounkpe | — |
| Mathieu Fronius | — |
| Daniel Bonnet | — |

---

## Licence

À définir.