from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).resolve().parents[1] / "kudos.db"


def _resolve_db_path(db_path: str | Path | None = None) -> Path:
    return Path(db_path) if db_path is not None else DB_PATH


@contextmanager
def _get_connection(db_path: str | Path | None = None) -> Iterator[sqlite3.Connection]:
    db_file = _resolve_db_path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def _to_row_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def _normalize_created_at(created_at: datetime | str | None) -> str:
    if created_at is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(created_at, datetime):
        return created_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return created_at


def init_db(db_path: str | Path | None = None) -> None:
    with _get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS kudos (
                id INTEGER PRIMARY KEY,
                from_user TEXT,
                to_user TEXT,
                message TEXT,
                category TEXT,
                created_at TIMESTAMP
            )
            """
        )
        connection.commit()


def give_kudos(
    from_user: str,
    to_user: str,
    message: str,
    category: str,
    created_at: datetime | str | None = None,
    db_path: str | Path | None = None,
) -> dict[str, Any]:
    init_db(db_path)
    created_at_value = _normalize_created_at(created_at)

    with _get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO kudos (from_user, to_user, message, category, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (from_user, to_user, message, category, created_at_value),
        )
        new_id = cursor.lastrowid
        connection.commit()

        row = connection.execute(
            """
            SELECT id, from_user, to_user, message, category, created_at
            FROM kudos
            WHERE id = ?
            """,
            (new_id,),
        ).fetchone()

    return dict(row) if row is not None else {}


def get_kudos_for_user(
    user: str,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    with _get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, from_user, to_user, message, category, created_at
            FROM kudos
            WHERE to_user = ?
            ORDER BY created_at DESC, id DESC
            """,
            (user,),
        ).fetchall()
    return _to_row_dicts(rows)


def get_leaderboard(
    limit: int | None = None,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    query = """
        SELECT to_user AS user, COUNT(*) AS kudos_count
        FROM kudos
        GROUP BY to_user
        ORDER BY kudos_count DESC, user ASC
    """
    params: tuple[Any, ...] = ()
    if limit is not None:
        query += "\nLIMIT ?"
        params = (limit,)

    with _get_connection(db_path) as connection:
        rows = connection.execute(query, params).fetchall()
    return _to_row_dicts(rows)


def get_recent(
    limit: int = 10,
    db_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    with _get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, from_user, to_user, message, category, created_at
            FROM kudos
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return _to_row_dicts(rows)
