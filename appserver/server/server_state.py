import threading
import logging
from enum import Enum

logger = logging.getLogger(__name__)


# 3 etats : actif (tout marche), lecture seule (juste consulter), desactive (rien)
class ServerStatus(Enum):
    ACTIVE = "active"
    READ_ONLY = "read_only"
    DISABLED = "disabled"


class ServerState:
    def __init__(self):
        self._status = ServerStatus.ACTIVE
        self._lock = threading.RLock()  # le statut est lu/ecrit par plusieurs threads

    @property
    def status(self):
        with self._lock:
            return self._status

    def set_status(self, new):
        with self._lock:
            old = self._status
            self._status = new
        logger.info(f"[SERVER] {old.value} -> {new.value}")

    def is_active(self):
        return self.status == ServerStatus.ACTIVE

    def is_read_only(self):
        return self.status == ServerStatus.READ_ONLY

    def is_disabled(self):
        return self.status == ServerStatus.DISABLED


server_state = ServerState()
