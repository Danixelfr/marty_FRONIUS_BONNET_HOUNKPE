"""
Calibration des couleurs du capteur de Marty — D-006.

Le capteur de couleur de Marty renvoie des valeurs RGB brutes qui dépendent
du robot, de l'éclairage et de la plaque utilisée. Ce module permet
d'associer ces valeurs mesurées aux codes couleur standard du jeu
(N, P, B, Y, C, G, R — cf. CLAUDE.md), afin que `RobotClient.lire_couleur()`
reconnaisse correctement la plaque sous le robot.

La calibration est enregistrée dans un fichier JSON (`calibration_couleurs.json`,
à la racine de l'application robot) et rechargée au démarrage. Si aucune
calibration n'a encore été enregistrée, des valeurs RGB approximatives par
défaut sont utilisées.
"""

import json
from pathlib import Path


# Codes couleur standard reconnus par le jeu, et leur nom affiché.
CODES_COULEURS: dict[str, str] = {
    "N": "Noir",
    "P": "Mauve",
    "B": "Bleu foncé",
    "Y": "Jaune",
    "C": "Bleu ciel",
    "G": "Vert",
    "R": "Rouge",
}

# Valeurs RGB par défaut (approximatives), utilisées tant qu'aucune
# calibration n'a été effectuée pour une couleur donnée.
COULEURS_PAR_DEFAUT: dict[str, tuple[int, int, int]] = {
    "N": (0, 0, 0),         # Noir
    "P": (128, 0, 128),     # Mauve
    "B": (0, 0, 139),       # Bleu foncé
    "Y": (255, 255, 0),     # Jaune
    "C": (135, 206, 235),   # Bleu ciel
    "G": (0, 128, 0),       # Vert
    "R": (255, 0, 0),       # Rouge
}

# Fichier de calibration, stocké à la racine de l'application robot
# (= dossier parent de ce module).
CHEMIN_CALIBRATION = Path(__file__).resolve().parent / "calibration_couleurs.json"


def charger_calibration() -> dict[str, tuple[int, int, int]]:
    """
    Charge la calibration depuis `calibration_couleurs.json`.

    Pour chaque couleur standard, utilise la valeur enregistrée si elle
    existe, sinon la valeur par défaut. Si le fichier est absent ou
    invalide, renvoie uniquement les valeurs par défaut.
    """
    calibration = dict(COULEURS_PAR_DEFAUT)

    if CHEMIN_CALIBRATION.exists():
        try:
            with open(CHEMIN_CALIBRATION, "r", encoding="utf-8") as f:
                data = json.load(f)
            for code, rgb in data.items():
                if code in calibration and isinstance(rgb, (list, tuple)) and len(rgb) == 3:
                    calibration[code] = tuple(int(v) for v in rgb)
        except (OSError, ValueError, json.JSONDecodeError):
            # Fichier corrompu ou illisible : on retombe sur les valeurs par défaut.
            pass

    return calibration


def sauvegarder_calibration(calibration: dict[str, tuple[int, int, int]]) -> None:
    """Enregistre la calibration dans `calibration_couleurs.json`."""
    data = {code: list(rgb) for code, rgb in calibration.items()}
    with open(CHEMIN_CALIBRATION, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
