def calculer_points(couleur_detectee, bras_actuels, expression_actuelle, toutes_les_regles):
    """
    Calcule le score total pour un mouvement donné.
    
    Paramètres:
    - couleur_detectee (str): 'N', 'B', ou 'R'
    - bras_actuels (list): Liste des positions des bras (ex: ['ALU', 'ARU'])
    - expression_actuelle (str): Code de l'expression (ex: 'XSD')
    - toutes_les_regles (dict): Le dictionnaire extrait du fichier .battle
    """

    regles_section = toutes_les_regles.get(couleur_detectee, [])
    score_total = 0

    etat_global = bras_actuels + [expression_actuelle]
    
    # 2. On analyse chaque règle une par une
    for regle in regles_section:
        condition_brute = regle["conditions"]
        valeur_points = regle["score"]
        
        # Cas A : Opérateur OR (virgule) - Au moins un élément doit être vrai
        if ',' in condition_brute:
            elements = [e.strip() for e in condition_brute.split(',')]
            if any(item in etat_global for item in elements):
                score_total += valeur_points
        
        # Cas B : Opérateur AND (+) - Tous les éléments doivent être vrais
        elif '+' in condition_brute:
            elements = [e.strip() for e in condition_brute.split('+')]
            if all(item in etat_global for item in elements):
                score_total += valeur_points
        
        # Cas C : Condition simple (un seul mouvement ou expression)
        else:
            if condition_brute.strip() in etat_global:
                score_total += valeur_points
                
    return score_total

# --- EXEMPLE DE TEST (Validation des critères) ---
regles_exemple = {
    "R": [
        {"conditions": "ALU+ARU", "score": 2},  # AND
        {"conditions": "XNG", "score": 3},      # Expression seule
        {"conditions": "XSD", "score": -2}      # Score négatif
    ],
    "B": [
        {"conditions": "ALB, ARB", "score": 1}  # OR
    ]
}

# Test : Robot sur Rouge, lève les deux bras (ALU + ARU) et est en colère (XNG)
resultat = calculer_points("R", ["ALU", "ARU"], "XNG", regles_exemple)
print(f"Points cumulés : {resultat}") # Doit afficher 5 (2 + 3)


