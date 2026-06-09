"""
Découverte automatique des robots Marty sur le réseau local.

Scan TCP parallèle du sous-réseau sur le port 80 (WebSocket Marty).
"""

import socket
import ipaddress
import concurrent.futures
from typing import Optional

MARTY_PORT = 80
SCAN_TIMEOUT = 0.3


def _get_local_subnet() -> Optional[ipaddress.IPv4Network]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
    except Exception:
        return None


def _port_ouvert(ip: str) -> Optional[str]:
    try:
        with socket.create_connection((ip, MARTY_PORT), timeout=SCAN_TIMEOUT):
            return ip
    except Exception:
        return None


class RobotDiscovery:
    """Recherche des robots Marty sur le réseau local via scan TCP."""

    def chercher(self) -> list[str]:
        subnet = _get_local_subnet()
        if subnet is None:
            return []

        hôtes = [str(h) for h in subnet.hosts()]
        trouvés = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
            for résultat in executor.map(_port_ouvert, hôtes):
                if résultat:
                    trouvés.append(résultat)

        return trouvés
