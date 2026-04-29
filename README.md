# marty_FRONIUS_BONNET_HOUNKPE

Projet 3A MARTY groupe TP2

## Description

Ce projet contient deux applications principales :
- **approbot** : Interface utilisateur PyQt pour l'application.
- **appserver** : Serveur HTTP pour les services backend.

## Installation

### Prérequis
- Python 3.8+
- Git

### Configuration de l'environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate  # Sur Windows
pip install -r requirements.txt
```

### Installation des dépendances
Pour approbot :
```bash
cd approbot
pip install -r requirements.txt
```

Pour appserver :
```bash
cd appserver
pip install -r requirements.txt
```

## Utilisation

### Démarrage du serveur
```bash
cd appserver
python app.py
```

### Lancement de l'interface
```bash
cd approbot
python main.py
```

## Workflow Git

- **Branche principale** : `main` (protégée, PR obligatoire)
- **Branche d'intégration** : `develop`
- **Branches de fonctionnalités** : `feature/[nom]-[description]`

### Démarrage d'une tâche
```bash
git checkout develop
git pull origin develop
git checkout -b feature/[votre-nom]-[tache]
```

## Contributeurs

- Joseph
- Mathieu
- Daniel

## Licence

[À définir]
