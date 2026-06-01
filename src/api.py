from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.models import (
    get_kudos_for_user,
    get_leaderboard,
    get_recent,
    give_kudos,
    init_db,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class GiveKudosRequest(BaseModel):
    from_user: str = Field(min_length=1)
    to_user: str = Field(min_length=1)
    message: str = Field(min_length=1)
    category: str = Field(min_length=1)


@app.post("/kudos")
def create_kudos(payload: GiveKudosRequest) -> dict[str, object]:
    return give_kudos(**payload.model_dump())


@app.get("/kudos/{user}")
def read_user_kudos(user: str) -> list[dict[str, object]]:
    return get_kudos_for_user(user)


@app.get("/leaderboard")
def read_leaderboard() -> list[dict[str, object]]:
    return get_leaderboard()


@app.get("/recent")
def read_recent() -> list[dict[str, object]]:
    return get_recent()
