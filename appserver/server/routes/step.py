import logging
from server.registry import registry
from server.battle_config import battle_config
from server.battle.evaluator import compute_points
from server.events import events

logger = logging.getLogger(__name__)


def handle_post_step(handler):
    body = handler._read_body()
    rid = body.get("rid")
    col = body.get("col", "")
    arm = body.get("arm", "")
    exp = body.get("exp", "")

    if not rid:
        handler.send_json(400, {"error": "rid requis"})
        return

    robot = registry.get(rid)
    if robot is None:
        handler.send_json(404, {"error": f"robot {rid} inconnu"})
        return

    if robot["state"] != "dancing":
        logger.warning(f"[STEP] {rid} pas en mode dancing (state={robot['state']})")

    if not col:
        handler.send_json(400, {"error": "col requis"})
        return

    rules = battle_config.rules.get(col, [])
    if not rules and battle_config.is_loaded:
        logger.warning(f"[STEP] Aucune regle pour couleur '{col}'")

    points = compute_points(rules, arm, exp)

    new_score = robot["score"] + points
    new_steps = robot["nb_steps_done"] + 1
    registry.update(
        rid,
        score=new_score,
        nb_steps_done=new_steps,
        last_step={"col": col, "arm": arm, "exp": exp, "points": points},
    )

    logger.info(
        f"[STEP] {rid} col={col} arm={arm or '-'} exp={exp} -> {points:+d} "
        f"(total: {new_score}, step {new_steps}/{robot['nb_steps_required']})"
    )

    events.add("step", rid=rid, col=col, arm=arm, exp=exp, points=points, score=new_score)
    handler.send_json(200, points)
