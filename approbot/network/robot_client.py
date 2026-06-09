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
    # Déplacements, bras, expressions → implémentés dans D-004
    # ------------------------------------------------------------------
