import json
import logging
from http.server import BaseHTTPRequestHandler
from os import path
from urllib.parse import urlparse, parse_qs

from .routes.version import handle_get_version
from .routes.hello import handle_post_hello
from .routes.start import handle_post_start
from .routes.step import handle_post_step
from .routes.score import handle_get_score
from .routes.bye import handle_post_bye

logger = logging.getLogger(__name__)



# Le requestHandler est la classe qui va gérer les requetes qui arrivent sur le serveur puis va les triater et repondre au client.
class RequestHandler(BaseHTTPRequestHandler):

    GET_ROUTES: dict = {}
    POST_ROUTES: dict = {}

    

    # permet d'envoyer une reponse au format json au client
    def send_json(self, code: int, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    #permet d'envoyer une reponse textuelle au client
    def send_text(self, code: int, text: str):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    #Lit le body POST, gère form-urlencoded et JSON
    
    def _read_body(self) -> dict:
        #length contiendra la taille du body de la requete, si elle est nulle on retourne un dict vide
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        #body contiendra le contenu du body de la requete, on le decode en utf-8
        body = self.rfile.read(length).decode("utf-8")
        #ctype contiera le type de contenu de la requete, on verifie si c'est du json ou du form-urlencoded
        ctype = self.headers.get("Content-Type", "")
        if "application/json" in ctype:
            return json.loads(body)
        
        # form-urlencoded par défaut
        parsed = parse_qs(body)
        return {k: v[0] for k, v in parsed.items()}




    #permet de gerer les requetes GET qui arrivent sur le serveur
    def do_GET(self):
        
        path = urlparse(self.path).path
        logger.info(f"[GET]{path}")
        chemin = self.GET_ROUTES.get(path)
        #si la requete est vide ou que le chemin n'est pas trouvé dans les routes, on retourne une erreur 404
        if chemin is None:
            self.send_json(404, {"error": f"GET{path} not found"})
            return
        try:
            chemin(self)
        except Exception as e:
            logger.exception("Handler error")
            self.send_json(500, {"error": str(e)})

    def do_POST(self):
        path = urlparse(self.path).path
        logger.info(f"[POST]{path}")
        chemin = self.POST_ROUTES.get(path)
        if chemin is None:
            self.send_json(404, {"error": f"POST{path} not found"})
            return
        try:
            chemin(self)
        except Exception as e:
            logger.exception("Handler error")
            self.send_json(500, {"error": str(e)})
    
    # On desactive les logs par défaut car on utilise nos propres logs à la place)
    def log_message(self, format, *args):
        
        pass

RequestHandler.GET_ROUTES["/"] = handle_get_version
RequestHandler.POST_ROUTES["/hello"] = handle_post_hello
RequestHandler.POST_ROUTES["/start"] = handle_post_start
RequestHandler.POST_ROUTES["/step"] = handle_post_step
RequestHandler.GET_ROUTES["/score"] = handle_get_score
RequestHandler.POST_ROUTES["/bye"] = handle_post_bye

