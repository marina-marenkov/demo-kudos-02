# Kudos API

Simple team recognition app built with **FastAPI + SQLite**. Coworkers can give each other kudos, see personal kudos history, a team leaderboard, and a recent activity feed.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

API base URL: `http://localhost:8000`

## API examples

### POST /kudos

```bash
curl -X POST "http://localhost:8000/kudos" \
  -H "Content-Type: application/json" \
  -d '{
    "from_user": "alice",
    "to_user": "bob",
    "message": "Great support on the release!",
    "category": "teamwork"
  }'
```

### GET /kudos/{user}

```bash
curl "http://localhost:8000/kudos/bob"
```

### GET /leaderboard

```bash
curl "http://localhost:8000/leaderboard"
```

### GET /recent

```bash
curl "http://localhost:8000/recent"
```

## CLI usage (no server needed)

The CLI talks directly to SQLite:

```bash
python -m src.cli give --from mike --to alice --msg "Great PR!" --category teamwork
python -m src.cli leaderboard
python -m src.cli recent
```

## Docker

Build image:

```bash
docker build -t kudos-api:latest .
```

Run container:

```bash
docker run --rm -p 8000:8000 kudos-api:latest
```
