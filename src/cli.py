from __future__ import annotations

import argparse
from collections.abc import Sequence

from src.models import get_leaderboard, get_recent, give_kudos, init_db


def _run_give(args: argparse.Namespace) -> int:
    created = give_kudos(
        from_user=args.from_user,
        to_user=args.to_user,
        message=args.msg,
        category=args.category,
    )
    print(
        f"Kudos sent (id={created['id']}): "
        f"{created['from_user']} -> {created['to_user']} "
        f"[{created['category']}] {created['message']}"
    )
    return 0


def _run_leaderboard(_args: argparse.Namespace) -> int:
    rows = get_leaderboard()
    if not rows:
        print("No kudos yet.")
        return 0

    for index, row in enumerate(rows, start=1):
        print(f"{index}. {row['user']} - {row['kudos_count']}")
    return 0


def _run_recent(_args: argparse.Namespace) -> int:
    rows = get_recent()
    if not rows:
        print("No kudos yet.")
        return 0

    for row in rows:
        print(
            f"{row['created_at']} | {row['from_user']} -> {row['to_user']} "
            f"[{row['category']}] {row['message']}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kudos command-line interface")
    subparsers = parser.add_subparsers(dest="command")

    give_parser = subparsers.add_parser("give", help="Give kudos to a teammate")
    give_parser.add_argument("--from", dest="from_user", required=True, help="Sender username")
    give_parser.add_argument("--to", dest="to_user", required=True, help="Recipient username")
    give_parser.add_argument("--msg", required=True, help="Kudos message")
    give_parser.add_argument("--category", required=True, help="Kudos category")
    give_parser.set_defaults(handler=_run_give)

    leaderboard_parser = subparsers.add_parser("leaderboard", help="Show kudos leaderboard")
    leaderboard_parser.set_defaults(handler=_run_leaderboard)

    recent_parser = subparsers.add_parser("recent", help="Show recent kudos")
    recent_parser.set_defaults(handler=_run_recent)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    init_db()
    return int(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
