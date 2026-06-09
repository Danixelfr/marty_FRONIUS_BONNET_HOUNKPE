import logging
from datetime import datetime
from server.registry import registry

logger = logging.getLogger(__name__)


def handle_post_bye(handler):
    body = handler._read_body()
    rid = body.get("rid")

    if not rid:
        handler.send_json(400, {"error": "rid requis"})
        return

    robot = registry.get(rid)
    if robot is None:
        logger.warning(f"[BYE] Robot {rid} deja deconnecte ou inconnu")
        handler.send_json(200, {"ok": True})
        return

    final_score = robot["score"]
    now = datetime.now().isoformat()
    registry.update(
        rid,
        state="disconnected",
        active=False,
        disconnected_at=now,
    )

    duration = (datetime.fromisoformat(now) - datetime.fromisoformat(robot["connected_at"])).total_seconds()
    logger.info(f"[BYE] {rid} : {robot['nb_steps_done']} pas, score={final_score}, duree={duration:.1f}s")

    handler.send_json(200, {"ok": True, "final_score": final_score})
