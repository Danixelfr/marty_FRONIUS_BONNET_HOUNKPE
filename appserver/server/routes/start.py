import logging
from server.registry import registry
from server.battle_config import battle_config
from server.events import events

logger = logging.getLogger(__name__)


def handle_post_start(handler):
    """POST /start → déclare le début de la chorégraphie et renvoie le MVS.

    Le nombre de mouvements (MVS) est fixé par le serveur/arbitre via le
    fichier .battle. Le robot adapte sa chorégraphie ; ici on renvoie juste
    l'entier attendu.
    """
    body = handler._read_body()
    rid = body.get("rid")

    if not rid:
        handler.send_json(400, {"error": "rid requis"})
        return

    robot = registry.get(rid)
    if robot is None:
        handler.send_json(404, {"error": f"robot {rid} inconnu"})
        return

    # Robot déjà en cours de danse → on relance proprement (restart)
    if robot["state"] == "dancing":
        logger.warning(f"[START] {rid} déjà en mode dancing → restart")

    mvs = battle_config.mvs

    registry.update(
        rid,
        state="dancing",
        nb_steps_required=mvs,
        nb_steps_done=0,
        score=0,
    )

    logger.info(f"[START] Robot {rid} démarre ({mvs} pas)")

    if not battle_config.is_loaded:
        logger.warning(
            f"[START] Aucun .battle chargé → utilisation du MVS par défaut ({mvs})"
        )

    events.add("start", rid=rid, mvs=mvs)
    handler.send_json(200, mvs)
