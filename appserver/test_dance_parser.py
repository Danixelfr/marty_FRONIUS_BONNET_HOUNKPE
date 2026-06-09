"""
Tests unitaires — dance_parser.py
Couvre tous les critères d'acceptation.
"""

import unittest
from dance_parser import (
    parse_dance,
    parse_dance_file,
    DanceProgram,
    Movement,
    ColorRule,
    DanceParseError,
)


EXAMPLE_DANCE = """\
SEQ 1
3U
2R
1B
4L
2U
1R
3B
ACT
R ARU ALB XNG
B XSD
N ARU ALB XNG
V ALD XHR
"""


class TestParseSeq(unittest.TestCase):
    """Critère : Parse SEQ X (ignore le numéro) + mouvements."""

    def setUp(self):
        self.prog = parse_dance(EXAMPLE_DANCE)


    def test_seq_id_parsed(self):
        """SEQ X : le numéro est bien capturé."""
        self.assertEqual(self.prog.seq_id, 1)

    def test_seq_movement_count(self):
        """7 mouvements attendus."""
        self.assertEqual(len(self.prog.movements), 7)

    def test_direction_U_forward(self):
        """3U → 3 pas, direction 'forward'."""
        m = self.prog.movements[0]
        self.assertEqual(m.steps, 3)
        self.assertEqual(m.direction, "forward")
        self.assertEqual(m.direction_raw, "U")

    def test_direction_R_right(self):
        """2R → 2 pas, direction 'right'."""
        m = self.prog.movements[1]
        self.assertEqual(m.steps, 2)
        self.assertEqual(m.direction, "right")

    def test_direction_B_backward(self):
        """1B → 1 pas, direction 'backward'."""
        m = self.prog.movements[2]
        self.assertEqual(m.steps, 1)
        self.assertEqual(m.direction, "backward")

    def test_direction_L_left(self):
        """4L → 4 pas, direction 'left'."""
        m = self.prog.movements[3]
        self.assertEqual(m.steps, 4)
        self.assertEqual(m.direction, "left")

    def test_all_movements_sequence(self):
        """Séquence complète : steps et directions dans l'ordre."""
        expected = [
            (3, "forward"),
            (2, "right"),
            (1, "backward"),
            (4, "left"),
            (2, "forward"),
            (1, "right"),
            (3, "backward"),
        ]
        result = [(m.steps, m.direction) for m in self.prog.movements]
        self.assertEqual(result, expected)


class TestParseAct(unittest.TestCase):
    """Critère : Parse section ACT avec règles couleur-expression."""

    def setUp(self):
        self.prog = parse_dance(EXAMPLE_DANCE)

    def test_act_rule_count(self):
        """4 règles ACT attendues."""
        self.assertEqual(len(self.prog.act_rules), 4)

    def test_rouge_actions_and_expression(self):
        """R ARU ALB XNG → couleur R, actions [ARU, ALB], expression XNG."""
        r = self.prog.act_rules[0]
        self.assertEqual(r.color, "R")
        self.assertEqual(r.actions, ["ARU", "ALB"])
        self.assertEqual(r.expression, "XNG")

    def test_bleu_expression_only(self):
        """B XSD → couleur B, pas d'action, expression XSD."""
        r = self.prog.act_rules[1]
        self.assertEqual(r.color, "B")
        self.assertEqual(r.actions, [])
        self.assertEqual(r.expression, "XSD")

    def test_noir_same_as_rouge(self):
        """N ARU ALB XNG → identique à R mais couleur N."""
        r = self.prog.act_rules[2]
        self.assertEqual(r.color, "N")
        self.assertEqual(r.actions, ["ARU", "ALB"])
        self.assertEqual(r.expression, "XNG")

    def test_vert_action_expression(self):
        """V ALD XHR → couleur V, action ALD, expression XHR."""
        r = self.prog.act_rules[3]
        self.assertEqual(r.color, "V")
        self.assertEqual(r.actions, ["ALD"])
        self.assertEqual(r.expression, "XHR")


class TestReturnTypes(unittest.TestCase):
    """Critère : format de retour utilisable par l'exécuteur."""

    def setUp(self):
        self.prog = parse_dance(EXAMPLE_DANCE)

    def test_returns_dance_program(self):
        self.assertIsInstance(self.prog, DanceProgram)

    def test_movements_are_movement_objects(self):
        for m in self.prog.movements:
            self.assertIsInstance(m, Movement)

    def test_rules_are_color_rule_objects(self):
        for r in self.prog.act_rules:
            self.assertIsInstance(r, ColorRule)

    def test_movement_fields_types(self):
        m = self.prog.movements[0]
        self.assertIsInstance(m.steps, int)
        self.assertIsInstance(m.direction, str)
        self.assertIsInstance(m.direction_raw, str)

    def test_color_rule_fields_types(self):
        r = self.prog.act_rules[0]
        self.assertIsInstance(r.color, str)
        self.assertIsInstance(r.actions, list)


class TestEdgeCases(unittest.TestCase):
    """Cas limites et robustesse."""

    def test_seq_number_ignored_functionally(self):
        """Le numéro SEQ est parsé mais n'affecte pas les mouvements."""
        prog = parse_dance("SEQ 99\n1U\nACT\nR XHR\n")
        self.assertEqual(prog.seq_id, 99)
        self.assertEqual(len(prog.movements), 1)

    def test_comments_and_blank_lines_ignored(self):
        src = "SEQ 1\n# commentaire\n\n2U\nACT\nR XHR\n"
        prog = parse_dance(src)
        self.assertEqual(len(prog.movements), 1)

    def test_invalid_movement_raises(self):
        with self.assertRaises(DanceParseError):
            parse_dance("SEQ 1\nXX\nACT\n")

    def test_missing_seq_raises(self):
        with self.assertRaises(DanceParseError):
            parse_dance("1U\n2L\nACT\nR XHR\n")

    def test_empty_act_is_valid(self):
        prog = parse_dance("SEQ 1\n1U\nACT\n")
        self.assertEqual(prog.act_rules, [])

    def test_file_parsing(self):
        """Critère : tests avec le fichier exemple sur disque."""
        prog = parse_dance_file("example.dance")
        self.assertEqual(prog.seq_id, 1)
        self.assertEqual(len(prog.movements), 7)
        self.assertEqual(len(prog.act_rules), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
