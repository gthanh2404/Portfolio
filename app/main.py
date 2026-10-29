"""Starter application for 72ITDS30103 Software Development Platforms.

Session 14, Task D: the database is reached through one small, self-healing pool.
"""

import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from psycopg_pool import ConnectionPool

APP_NAME = os.getenv("APP_NAME", "sdp-starter")
APP_VERSION = "1.3.0"  # Task D: the visible change for this pull request
APP_ENV = os.environ.get("APP_ENV", "development")
DATABASE_URL = os.environ["DATABASE_URL"]  # crash at start if it is missing

# One pool per running copy of the app. Created closed: tests can import this
# file without a database; the server opens it at start-up (lifespan below).
pool = ConnectionPool(
    DATABASE_URL,
    min_size=1,
    max_size=5,  # small pool: several copies run
    max_lifetime=300,  # recycle: replace after 5 minutes
    check=ConnectionPool.check_connection,  # pre-ping: test before lending
    kwargs={
        "prepare_threshold": None,  # port 6543: no prepared statements
        "connect_timeout": 5,  # fail fast instead of hanging
    },
    open=False,
)


@asynccontextmanager
async def lifespan(app):
    pool.open()  # does not wait: the app starts even if the database is paused
    yield
    pool.close()  # Render stops the container: return the connections cleanly


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)

# In-memory data from the starter (kept for the existing tests).
ITEMS = [
    {"id": 1, "name": "Write a Dockerfile", "done": False},
    {"id": 2, "name": "Run it with Compose", "done": False},
    {"id": 3, "name": "Deploy it to Render", "done": False},
]


@app.get("/")
def root():
    """Proves the app is reachable. Open /docs for the interactive API page."""
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "env": APP_ENV,
        "message": "Hello from the starter app",
    }


@app.get("/health")
def health():
    """Fast, no login, touches nothing. Render's health check path points here."""
    return {"status": "ok"}


@app.get("/items")
def list_items():
    return ITEMS


@app.get("/items/{item_id}")
def get_item(item_id: int):
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/health/db")
def health_db():
    """Proves the database works. Borrows a connection from the pool for one query."""
    try:
        with pool.connection(timeout=5) as conn:
            n = conn.execute("SELECT count(*) FROM notes").fetchone()[0]
        return {"db": "ok", "notes": n}
    except psycopg.Error as err:  # includes PoolTimeout when the database is paused
        print("health/db failed:", type(err).__name__, err)  # details to the logs only
        return JSONResponse(status_code=503, content={"db": "error"})
