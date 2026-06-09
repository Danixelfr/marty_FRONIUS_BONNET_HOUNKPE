import logging
from urllib.parse import urlparse, parse_qs
from server.registry import registry

logger = logging.getLogger(__name__)


def handle_get_score(handler):
    qs = parse_qs(urlparse(handler.path).query)
    rid = qs.get("rid", [None])[0]

    if not rid:
        handler.send_json(400, {"error": "rid requis (query string ?rid=...)"})
        return

    robot = registry.get(rid)
    if robot is None:
        handler.send_json(404, {"error": f"robot {rid} inconnu"})
        return

    score = robot["score"]
    logger.info(f"[SCORE] {rid} -> {score}")
    handler.send_json(200, score)
