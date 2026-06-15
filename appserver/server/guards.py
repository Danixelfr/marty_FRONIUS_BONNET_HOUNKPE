from server.server_state import server_state, ServerStatus

# GET / repond toujours, sinon le robot croit que le serveur est mort
ALWAYS_OPEN = {"GET /"}
# en lecture seule on autorise juste consulter le score et se deconnecter
READ_OPS = {"GET /score", "POST /bye"}


def is_allowed(method, path):
    key = f"{method} {path}"
    if key in ALWAYS_OPEN:
        return True
    status = server_state.status
    if status == ServerStatus.ACTIVE:
        return True
    if status == ServerStatus.READ_ONLY and key in READ_OPS:
        return True
    return False
