import threading

from calibration_couleurs import charger_calibration, COULEURS_PAR_DEFAUT


class RobotClient:
    """Wrapper martypy pour le robot Marty physique."""

    def __init__(self):
        self.marty = None
        # Verrou protégeant l'accès à `self.marty` : plusieurs threads
        # (interface, ExecuteurChoregraphie, ReleveEtatRobot - D-005)
        # peuvent appeler des méthodes du robot en même temps, et martypy
        # n'est pas garanti thread-safe pour des appels concurrents.
        self._lock = threading.Lock()
        # Calibration couleur (D-006) : association valeurs RGB mesurées
        # <-> codes couleur standard (N, P, B, Y, C, G, R).
        self.calibration: dict[str, tuple[int, int, int]] = charger_calibration()

    # ------------------------------------------------------------------
    # Connexion / Déconnexion
    # ------------------------------------------------------------------

    def connect(self, ip: str) -> None:
        """Connexion au robot via Wi-Fi."""
        import martypy  # import tardif : martypy n'est requis qu'à la connexion
        with self._lock:
            self.marty = martypy.Marty("wifi", ip)

    def disconnect(self) -> None:
        """Déconnexion propre du robot."""
        with self._lock:
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
        with self._lock:
            self.marty.walk(num_steps=nb_pas, step_length=30, move_time=1500)

    def reculer(self, nb_pas: int = 1) -> None:
        self._check()
        with self._lock:
            self.marty.walk(num_steps=nb_pas, step_length=-30, move_time=1500)

    def aller_gauche(self, nb_pas: int = 1) -> None:
        self._check()
        with self._lock:
            for _ in range(nb_pas):
                self.marty.sidestep(side="left", step_length=35, move_time=1500)

    def aller_droite(self, nb_pas: int = 1) -> None:
        self._check()
        with self._lock:
            for _ in range(nb_pas):
                self.marty.sidestep(side="right", step_length=35, move_time=1500)

    # ------------------------------------------------------------------
    # Bras
    # ------------------------------------------------------------------

    def lever_bras_gauche(self) -> None:  # ALU
        self._check()
        with self._lock:
            self.marty.arms(left_angle=100, right_angle=0, move_time=500)

    def lever_bras_droit(self) -> None:  # ARU
        self._check()
        with self._lock:
            self.marty.arms(left_angle=0, right_angle=100, move_time=500)

    def bras_gauche_arriere(self) -> None:  # ALB
        self._check()
        with self._lock:
            self.marty.arms(left_angle=-100, right_angle=0, move_time=500)

    def bras_droit_arriere(self) -> None:  # ARB
        self._check()
        with self._lock:
            self.marty.arms(left_angle=0, right_angle=-100, move_time=500)

    def bras_neutres(self) -> None:
        self._check()
        with self._lock:
            self.marty.arms(left_angle=0, right_angle=0, move_time=500)

    # ------------------------------------------------------------------
    # Expressions (poses martypy valides : angry, excited, wide, normal, wiggle)
    # ------------------------------------------------------------------

    def expression_neutre(self) -> None:  # XNT
        self._check()
        with self._lock:
            self.marty.eyes(pose_or_angle="normal", move_time=300)

    def expression_triste(self) -> None:  # XSD
        self._check()
        with self._lock:
            self.marty.eyes(pose_or_angle="wide", move_time=300)

    def expression_colere(self) -> None:  # XNG
        self._check()
        with self._lock:
            self.marty.eyes(pose_or_angle="angry", move_time=300)

    def expression_content(self) -> None:  # XHP
        self._check()
        with self._lock:
            self.marty.eyes(pose_or_angle="excited", move_time=300)

    def expression_enjoue(self) -> None:  # XDN
        self._check()
        with self._lock:
            self.marty.eyes(pose_or_angle="wiggle", move_time=300)

    # ------------------------------------------------------------------
    # Détection de couleur
    # ------------------------------------------------------------------

    # Référence RGB par défaut (avant calibration). Conservé pour
    # compatibilité ; voir calibration_couleurs.py pour la calibration
    # effectivement utilisée par lire_couleur() (self.calibration).
    COULEURS_REF: dict[str, tuple[int, int, int]] = COULEURS_PAR_DEFAUT

    def lire_couleur_brute(self) -> tuple[int, int, int] | None:
        """
        Lit la valeur RGB brute renvoyée par le capteur de couleur du robot,
        sans conversion vers un code couleur standard.

        Renvoie None si la lecture échoue (capteur indisponible, API
        différente, robot non connecté, ...).
        """
        self._check()
        try:
            with self._lock:
                hex_color = self.marty.get_color_sensor_hex("left")
            hex_color = str(hex_color).lstrip("#")
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except Exception:
            return None

    def lire_couleur(self) -> str:
        """
        Lit la couleur de la plaque sous le robot et renvoie le code
        couleur standard le plus proche (N, P, B, Y, C, G, R), d'après la
        calibration enregistrée (cf. calibration_couleurs.py).
        """
        rgb = self.lire_couleur_brute()
        if rgb is None:
            # Capteur indisponible / API différente : couleur par défaut
            return "N"

        return min(
            self.calibration,
            key=lambda code: sum(
                (a - b_) ** 2 for a, b_ in zip(self.calibration[code], rgb)
            ),
        )

    def recharger_calibration(self) -> None:
        """
        Recharge la calibration des couleurs depuis
        `calibration_couleurs.json` (appelé après modification via le
        dialogue de calibration — cf. calibration_dialog.py).
        """
        self.calibration = charger_calibration()

    # ------------------------------------------------------------------
    # Batterie (D-005)
    # ------------------------------------------------------------------

    def lire_batterie(self) -> float | None:
        """
        Renvoie le pourcentage de batterie restante du robot (0-100),
        ou None si la lecture échoue (capteur indisponible, robot V1, ...).
        """
        self._check()
        try:
            with self._lock:
                return float(self.marty.get_battery_remaining())
        except Exception:
            return None

    def _check(self) -> None:
        if self.marty is None:
            raise RuntimeError(
                "Robot non connecté. Appelez connect(ip) d'abord."
            )
