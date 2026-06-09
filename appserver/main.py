import argparse
import logging
from server.http_server import DanceBattleServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--battle", default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    #ameilloration et config des logs
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s]%(name)s :%(message)s",
        datefmt="%H:%M:%S",
    )

    if args.battle:
        from server.battle.parser import load_battle_file
        mvs, rules = load_battle_file(args.battle)
        logging.getLogger(__name__).info(f"Battle charge : {args.battle} (MVS={mvs}, couleurs={list(rules)})")

    server = DanceBattleServer(host=args.host, port=args.port)
    server.start()


if __name__ == "__main__":
    main()