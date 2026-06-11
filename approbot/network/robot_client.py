class RobotClient:
    """Wrapper martypy pour le robot Marty physique."""

    def __init__(self):
        self.marty = None

    # ------------------------------------------------------------------
    # Connexion / Déconnexion
    # ------------------------------------------------------------------

    def connect(self, ip: str) -> None:
        """Connexion au robot via Wi-Fi."""
        import martypy  # import tardif : martypy n'est requis qu'à la connexion
        self.marty = martypy.Marty("wifi", ip)

    def disconnect(self) -> None:
        """Déconnexion propre du robot."""
        if self.marty is not None:
            self.marty.close()
            self.marty = None

    @property
    def is_connected(self) -> bool:
        return self.marty is not None

    # ------------------------------------------------------------------
    # Déplacements
    # ------------------------------------------------------------------

    def avancer(self, nb_pas: int = 1) -> None:
        self._check()
        self.marty.walk(num_steps=nb_pas, step_length=30, move_time=1500)

    def reculer(self, nb_pas: int = 1) -> None:
        self._check()
        self.marty.walk(num_steps=nb_pas, step_length=-30, move_time=1500)

    def aller_gauche(self, nb_pas: int = 1) -> None:
        self._check()
        for _ in range(nb_pas):
            self.marty.sidestep(side="left", step_length=35, move_time=1500)

    def aller_droite(self, nb_pas: int = 1) -> None:
        self._check()
        for _ in range(nb_pas):
            self.marty.sidestep(side="right", step_length=35, move_time=1500)

    # ------------------------------------------------------------------
    # Bras
    # ------------------------------------------------------------------

    def lever_bras_gauche(self) -> None:  # ALU
        self._check()
        self.marty.arms(left_angle=100, right_angle=0, move_time=500)

    def lever_bras_droit(self) -> None:  # ARU
        self._check()
        self.marty.arms(left_angle=0, right_angle=100, move_time=500)

    def bras_gauche_arriere(self) -> None:  # ALB
        self._check()
        self.marty.arms(left_angle=-100, right_angle=0, move_time=500)

    def bras_droit_arriere(self) -> None:  # ARB
        self._check()
        self.marty.arms(left_angle=0, right_angle=-100, move_time=500)

    def bras_neutres(self) -> None:
        self._check()
        self.marty.arms(left_angle=0, right_angle=0, move_time=500)

    # ------------------------------------------------------------------
    # Expressions (poses martypy valides : angry, excited, wide, normal, wiggle)
    # ------------------------------------------------------------------

    def expression_neutre(self) -> None:  # XNT
        self._check()
        self.marty.eyes(pose_or_angle="normal", move_time=300)

    def expression_triste(self) -> None:  # XSD
        self._check()
        self.marty.eyes(pose_or_angle="wide", move_time=300)

    def expression_colere(self) -> None:  # XNG
        self._check()
        self.marty.eyes(pose_or_angle="angry", move_time=300)

    def expression_content(self) -> None:  # XHP
        self._check()
        self.marty.eyes(pose_or_angle="excited", move_time=300)

    def expression_enjoue(self) -> None:  # XDN
        self._check()
        self.marty.eyes(pose_or_angle="wiggle", move_time=300)

    # ------------------------------------------------------------------
    # Détection de couleur
    # ------------------------------------------------------------------

    # Couleurs standard et leur référence RGB approximative.
    # NOTE : première version du mapping, à calibrer avec les vraies
    # plaques (cf. issue "association couleur brute -> couleur standard").
    COULEURS_REF: dict[str, tuple[int, int, int]] = {
        "N": (0, 0, 0),         # Noir
        "P": (128, 0, 128),     # Mauve
        "B": (0, 0, 139),       # Bleu foncé
        "Y": (255, 255, 0),     # Jaune
        "C": (135, 206, 235),   # Bleu ciel
        "G": (0, 128, 0),       # Vert
        "R": (255, 0, 0),       # Rouge
    }

    def lire_couleur(self) -> str:
        """
        Lit la couleur de la plaque sous le robot et renvoie le code
        couleur standard le plus proche (N, P, B, Y, C, G, R).
        """
        self._check()
        try:
            valeurs = self.marty.get_color_sensor_values("left")
            r, g, b = valeurs["r"], valeurs["g"], valeurs["b"]
        except Exception:
            # Capteur indisponible / API différente : couleur par défaut
            return "N"

        return min(
            self.COULEURS_REF,
            key=lambda code: sum(
                (a - b_) ** 2 for a, b_ in zip(self.COULEURS_REF[code], (r, g, b))
            ),
        )

    def _check(self) -> None:
        if self.marty is None:
            raise RuntimeError(
                "Robot non connecté. Appelez connect(ip) d'abord."
            )
