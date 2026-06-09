import requests


class ServerClient:
    """Client HTTP pour communiquer avec l'application serveur/arbitre."""

    def __init__(self, host: str):
        """
        :param host: adresse du serveur, ex: "192.168.0.1:8080"
        """
        self.base_url = f"http://{host}"
        self.rid: str | None = None

    
    # GET /
    # Vérifie que le serveur est disponible. Renvoie la version (str).
    
    def ping(self) -> str:
        response = requests.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.text.strip()

    
    # POST /hello
    # Enregistre le robot. Renvoie l'identifiant unique (rid).
    
    def hello(self) -> str:
        response = requests.post(f"{self.base_url}/hello")
        response.raise_for_status()
        self.rid = response.text.strip()
        return self.rid

    
    # POST /start
    # Déclare le démarrage d'une chorégraphie.
    # Renvoie le nombre de pas à effectuer (int).
    
    def start(self) -> int:
        self._check_rid()
        response = requests.post(f"{self.base_url}/start", data={"rid": self.rid})
        response.raise_for_status()
        return int(response.text.strip())

   
    # POST /step
    # Envoie un pas effectué par le robot.
    #   col : couleur relevée        ex: "G"
    #   arm : mouvement de bras      ex: "ALU+ARU"
    #   exp : expression réalisée    ex: "XNT"
    # Renvoie le nombre de points obtenus pour ce pas (int).
    
    def step(self, col: str, arm: str, exp: str) -> int:
        self._check_rid()
        response = requests.post(
            f"{self.base_url}/step",
            data={"rid": self.rid, "col": col, "arm": arm, "exp": exp},
        )
        response.raise_for_status()
        return int(response.text.strip())

    
    # GET /score
    # Récupère le score total du robot (int).
    
    def score(self) -> int:
        self._check_rid()
        response = requests.get(
            f"{self.base_url}/score", params={"rid": self.rid}
        )
        response.raise_for_status()
        return int(response.text.strip())

    
    # POST /bye
    # Déconnecte le robot du serveur.
    
    def bye(self) -> None:
        self._check_rid()
        response = requests.post(f"{self.base_url}/bye", data={"rid": self.rid})
        response.raise_for_status()
        self.rid = None

    
    # Utilitaire interne
    
    def _check_rid(self) -> None:
        if self.rid is None:
            raise RuntimeError(
                "Robot non connecté. Appelez hello() avant toute autre méthode."
            )
