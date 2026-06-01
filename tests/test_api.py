from __future__ import annotations

import asyncio
import re
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

import src.models as models
from src.api import app


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> Path:
    db_dir = Path(__file__).resolve().parent / ".pytest_dbs"
    db_dir.mkdir(exist_ok=True)

    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid)
    db_path = db_dir / f"{safe_name}.sqlite3"

    if db_path.exists():
        db_path.unlink()

    monkeypatch.setattr(models, "DB_PATH", db_path)
    models.init_db()

    yield db_path

    if db_path.exists():
        db_path.unlink()


def test_create_kudos() -> None:
    payload = {
        "from_user": "alice",
        "to_user": "bob",
        "message": "Great support!",
        "category": "teamwork",
    }

    async def _run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post("/kudos", json=payload)

    response = asyncio.run(_run())

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("id"), int)
    assert data["from_user"] == payload["from_user"]
    assert data["to_user"] == payload["to_user"]
    assert data["message"] == payload["message"]
    assert data["category"] == payload["category"]


def test_get_leaderboard() -> None:
    with TestClient(app) as client:
        assert client.post(
            "/kudos",
            json={"from_user": "alice", "to_user": "bob", "message": "Great docs", "category": "teamwork"},
        ).status_code == 200
        assert client.post(
            "/kudos",
            json={
                "from_user": "carol",
                "to_user": "bob",
                "message": "Thanks for helping",
                "category": "helpfulness",
            },
        ).status_code == 200
        assert client.post(
            "/kudos",
            json={"from_user": "dave", "to_user": "amy", "message": "Great review", "category": "quality"},
        ).status_code == 200

        response = client.get("/leaderboard")

    assert response.status_code == 200
    assert response.json() == [
        {"user": "bob", "kudos_count": 2},
        {"user": "amy", "kudos_count": 1},
    ]


def test_get_user_kudos() -> None:
    async def _run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            assert (
                await client.post(
                    "/kudos",
                    json={
                        "from_user": "alice",
                        "to_user": "bob",
                        "message": "Great support",
                        "category": "teamwork",
                    },
                )
            ).status_code == 200
            assert (
                await client.post(
                    "/kudos",
                    json={
                        "from_user": "carol",
                        "to_user": "bob",
                        "message": "Great mentoring",
                        "category": "mentorship",
                    },
                )
            ).status_code == 200
            assert (
                await client.post(
                    "/kudos",
                    json={
                        "from_user": "dave",
                        "to_user": "amy",
                        "message": "Great design",
                        "category": "design",
                    },
                )
            ).status_code == 200

            return await client.get("/kudos/bob")

    response = asyncio.run(_run())

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {item["message"] for item in data} == {"Great support", "Great mentoring"}


def test_get_recent() -> None:
    with TestClient(app) as client:
        assert client.post(
            "/kudos",
            json={"from_user": "alice", "to_user": "bob", "message": "Great support", "category": "teamwork"},
        ).status_code == 200
        response = client.get("/recent")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Great support"


def test_invalid_input_returns_422() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/kudos",
            json={"from_user": "", "to_user": "bob", "message": "Great support", "category": "teamwork"},
        )
        response_missing_field = client.post(
            "/kudos",
            json={"to_user": "bob", "message": "Great support", "category": "teamwork"},
        )

    assert response.status_code == 422
    assert response_missing_field.status_code == 422
