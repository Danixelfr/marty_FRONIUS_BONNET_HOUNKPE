import logging
from server.registry import registry

logger = logging.getLogger(__name__)


def handle_post_hello(handler):
    """POST /hello → enregistre un robot et renvoie son rid."""
    rid = registry.register()
    logger.info(f"[HELLO] Nouveau robot enregistré : {rid}")
    handler.send_text(200, rid)