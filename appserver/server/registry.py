import uuid
from datetime import datetime
from typing import Optional


class RobotRegistry:
    """Registre des robots connectés."""

    def __init__(self):
        self._robots: dict[str, dict] = {}

    def register(self) -> str:
        """Crée un nouveau robot et renvoie son rid."""
        rid = uuid.uuid4().hex[:6].upper()
        self._robots[rid] = {
            "rid": rid,
            "score": 0,
            "state": "connected",       # connected | dancing | disconnected
            "connected_at": datetime.now().isoformat(),
            "disconnected_at": None,
            "nb_steps_required": None,  # rempli par /start
            "nb_steps_done": 0,
            "active": True,
            "last_step": None,          # dernier (col, arm, exp, points)
        }
        return rid

    def get(self, rid: str) -> Optional[dict]:
        return self._robots.get(rid)

    def exists(self, rid: str) -> bool:
        return rid in self._robots

    def all(self) -> list[dict]:
        return list(self._robots.values())

    def update(self, rid: str, **kwargs) -> bool:
        if rid not in self._robots:
            return False
        self._robots[rid].update(kwargs)
        return True


# Singleton partagé par tout le serveur
registry = RobotRegistry()
