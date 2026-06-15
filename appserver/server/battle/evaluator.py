import logging

logger = logging.getLogger(__name__)

# bras (ALU = bras gauche leve, ALB = bras gauche baisse...) et expressions du visage
ARM_TOKENS = {"ALU", "ARU", "ALB", "ARB"}
EXP_TOKENS = {"XNT", "XSD", "XNG", "XHP", "XDN"}


def parse_arms(arm_field):
    if not arm_field:
        return set()
    # en form-urlencoded le "+" devient un espace, donc on coupe sur les deux
    return {part for part in arm_field.replace("+", " ").split() if part}


def is_token_active(token, arms, exp):
    if token in ARM_TOKENS:
        return token in arms
    if token in EXP_TOKENS:
        return token == exp
    logger.warning(f"Token inconnu : {token}")
    return False


def normalize_rule(rule):
    # le parser donne un dict {"conditions","score"}, mais on accepte aussi un tuple deja pret
    if isinstance(rule, dict):
        conditions = rule.get("conditions", "")
        points = rule.get("score", 0)
        if "+" in conditions:  # + = ET
            tokens = [t.strip() for t in conditions.split("+") if t.strip()]
            return "AND", tokens, points
        if "," in conditions:  # , = OU
            tokens = [t.strip() for t in conditions.split(",") if t.strip()]
            return "OR", tokens, points
        return "SINGLE", [conditions.strip()], points
    op, tokens, points = rule
    return op, list(tokens), points


def evaluate_rule(rule, arms, exp):
    op, tokens, points = normalize_rule(rule)

    if op == "SINGLE" or op == "AND":
        if all(is_token_active(t, arms, exp) for t in tokens):
            return points
        return 0

    if op == "OR":
        # on compte les points une seule fois meme si plusieurs conditions sont vraies
        if any(is_token_active(t, arms, exp) for t in tokens):
            return points
        return 0

    logger.warning(f"Operateur inconnu : {op}")
    return 0


def compute_points(rules_for_color, arm, exp):
    arms = parse_arms(arm)
    total = 0
    for rule in rules_for_color:
        total += evaluate_rule(rule, arms, exp)
    return total
