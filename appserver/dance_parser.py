"""
Parser pour fichier .dance
Extrait la séquence de mouvements (SEQ) et les règles d'action par couleur (ACT).
"""

from dataclasses import dataclass, field
from typing import Optional
import re


# ---------------------------------------------------------------------------
# Structures de données
# ---------------------------------------------------------------------------

DIRECTION_MAP = {
    "U": "forward",
    "B": "backward",
    "L": "left",
    "R": "right",
}

@dataclass
class Movement:
    direction: str      # 'forward' | 'backward' | 'left' | 'right'
    direction_raw: str  # 'U' | 'B' | 'L' | 'R'
    steps: int

    def __repr__(self):
        return f"Movement(steps={self.steps}, direction='{self.direction}')"


@dataclass
class ColorRule:
    color: str          # lettre de couleur : 'R', 'B', 'N', 'V', ...
    actions: list[str]  # ex. ['ARU', 'ALB']
    expression: Optional[str] = None  # dernière token si préfixe 'X'

    def __repr__(self):
        return (
            f"ColorRule(color='{self.color}', "
            f"actions={self.actions}, expression={self.expression!r})"
        )


@dataclass
class DanceProgram:
    seq_id: int
    movements: list[Movement] = field(default_factory=list)
    act_rules: list[ColorRule] = field(default_factory=list)

    def __repr__(self):
        lines = [f"DanceProgram(seq_id={self.seq_id})"]
        lines.append(f"  SEQ ({len(self.movements)} mouvements):")
        for m in self.movements:
            lines.append(f"    {m}")
        lines.append(f"  ACT ({len(self.act_rules)} règles):")
        for r in self.act_rules:
            lines.append(f"    {r}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class DanceParseError(ValueError):
    pass


def _parse_movement(token: str, lineno: int) -> Movement:
    """Parse un token de mouvement, ex. '3U', '1L'."""
    m = re.fullmatch(r"(\d+)([UBLR])", token)
    if not m:
        raise DanceParseError(
            f"Ligne {lineno}: mouvement invalide '{token}' "
            f"(attendu : <nombre><direction>, ex. '3U')"
        )
    steps = int(m.group(1))
    raw = m.group(2)
    if steps <= 0:
        raise DanceParseError(f"Ligne {lineno}: nombre de pas doit être > 0, got {steps}")
    return Movement(direction=DIRECTION_MAP[raw], direction_raw=raw, steps=steps)


def _parse_color_rule(parts: list[str], lineno: int) -> ColorRule:
    """
    Parse une ligne ACT : <COULEUR> <TOKEN1> <TOKEN2> ... [<XTOKEN>]
    Les tokens commençant par 'X' sont traités comme expression.
    """
    if len(parts) < 2:
        raise DanceParseError(
            f"Ligne {lineno}: règle ACT incomplète '{' '.join(parts)}'"
        )
    color = parts[0]
    tokens = parts[1:]
    actions = []
    expression = None
    for tok in tokens:
        if tok.startswith("X"):
            expression = tok
        else:
            actions.append(tok)
    return ColorRule(color=color, actions=actions, expression=expression)


def parse_dance(source: str) -> DanceProgram:
    """
    Parse le contenu textuel d'un fichier .dance.
    Retourne un DanceProgram utilisable par l'exécuteur.
    """
    lines = source.splitlines()
    seq_id: Optional[int] = None
    movements: list[Movement] = []
    act_rules: list[ColorRule] = []

    section = None   # 'SEQ' | 'ACT'

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # --- En-tête SEQ ---
        if line.upper().startswith("SEQ"):
            parts = line.split()
            try:
                seq_id = int(parts[1]) if len(parts) > 1 else 1
            except ValueError:
                raise DanceParseError(
                    f"Ligne {lineno}: numéro SEQ invalide dans '{line}'"
                )
            section = "SEQ"
            continue

        # --- En-tête ACT ---
        if line.upper() == "ACT":
            section = "ACT"
            continue

        # --- Contenu selon la section ---
        if section == "SEQ":
            movements.append(_parse_movement(line, lineno))

        elif section == "ACT":
            parts = line.split()
            act_rules.append(_parse_color_rule(parts, lineno))

        else:
            raise DanceParseError(
                f"Ligne {lineno}: contenu hors section (SEQ/ACT) : '{line}'"
            )

    if seq_id is None:
        raise DanceParseError("Fichier .dance invalide : section SEQ introuvable")

    return DanceProgram(seq_id=seq_id, movements=movements, act_rules=act_rules)


def parse_dance_file(path: str) -> DanceProgram:
    """Lit un fichier .dance depuis le disque et le parse."""
    with open(path, "r", encoding="utf-8") as f:
        return parse_dance(f.read())
    

