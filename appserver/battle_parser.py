import re
def parser_battle(fichier_path):
    with open(fichier_path, 'r', encoding='utf-8') as f:
        contenu = f.read()
    mvs_match=re.search(r"MVS\s*(\d+)", contenu)
    mvs =int(mvs_match.group(1)) if mvs_match else 0

    sections= re.findall(r"\[([A-Z])\]\n([^\[]+)", contenu, re.DOTALL)
    resultats = {"MVS": mvs, "regles":{}}
    for couleur, bloc in sections:
        resultats["regles"][couleur]=[]
        lignes = bloc.strip().split('\n')
        for ligne in lignes:
            if '=' in ligne:
                conditions, score = ligne.split('=')
                resultats["regles"][couleur].append({"conditions": conditions.strip(), "score":int(score.strip())})
    return resultats


data= parser_battle(r"test_battle.battle")
print(data)
