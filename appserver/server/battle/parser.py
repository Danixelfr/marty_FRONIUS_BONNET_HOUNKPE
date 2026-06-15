import re
from server.battle_config import battle_config


def parse_battle(content):
    content = content.replace("\r\n", "\n")  # fichiers windows
    mvs_match = re.search(r"MVS\s*(\d+)", content)
    mvs = int(mvs_match.group(1)) if mvs_match else 0

    # chaque section [X] = une couleur, chaque ligne "conditions=points" = une regle
    rules = {}
    for color, block in re.findall(r"\[([A-Z])\]\n([^\[]+)", content, re.DOTALL):
        rules[color] = []
        for line in block.strip().splitlines():
            line = line.strip()
            if "=" in line:
                conditions, score = line.split("=", 1)
                rules[color].append({"conditions": conditions.strip(), "score": int(score.strip())})
    return mvs, rules


def parse_battle_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return parse_battle(f.read())


def load_battle_file(path):
    # parse le fichier puis range les regles dans battle_config (partage par tout le serveur)
    mvs, rules = parse_battle_file(path)
    battle_config.load(mvs, rules, path)
    return mvs, rules
