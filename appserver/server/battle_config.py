import threading


class BattleConfig:
    """État global du fichier .battle chargé.

    Le serveur est un ThreadingHTTPServer : plusieurs requêtes peuvent
    lire/écrire cet état en parallèle, d'où le verrou (RLock).
    """

    DEFAULT_MVS = 10  # valeur utilisée tant qu'aucun fichier .battle n'est chargé

    def __init__(self):
        self._lock = threading.RLock()
        self._mvs: int = self.DEFAULT_MVS
        self._rules: dict = {}          # rempli par le parser .battle (J-002)
        self._loaded_path: str | None = None

    def load(self, mvs: int, rules: dict, path: str = ""):
        """Charge la config d'un fichier .battle parsé."""
        with self._lock:
            self._mvs = mvs
            self._rules = rules
            self._loaded_path = path

    @property
    def mvs(self) -> int:
        with self._lock:
            return self._mvs

    @property
    def rules(self) -> dict:
        with self._lock:
            return dict(self._rules)

    @property
    def is_loaded(self) -> bool:
        with self._lock:
            return self._loaded_path is not None


# Singleton partagé par tout le serveur (comme registry)
battle_config = BattleConfig()
