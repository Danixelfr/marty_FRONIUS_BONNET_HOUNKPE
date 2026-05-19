from ..version import PROTOCOL_VERSION

"""Ce module contient les routes liées à la version de l'application et du protocole."""

def handle_get_version(handler):
    handler.send_text(200, PROTOCOL_VERSION)