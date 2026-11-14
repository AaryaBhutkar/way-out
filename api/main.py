"""Way Out API.

Run from the repo root:   uv run --project api uvicorn api.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import live, workers
from api.core import db as dbmod
from api.core.config import VERSION, get_settings
from api.routes import (
    agent,
    assignments,
    calls,
    hazards,
    health,
    households,
    plans,
    ride_requests,
    roads,
    sim,
    system,
    vehicles,
    zones,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

ROUTERS = [
    # core (Prem → Yash)
    health,
    households,
    ride_requests,
    assignments,
    live,
    # resident side (Deep)
    agent,
    calls,
    zones,
    system,
    # responder side (Yash)
    plans,
    vehicles,
    roads,
    hazards,
    sim,
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = dbmod.get_db()
    await dbmod.ensure_indexes(db)
    tasks = workers.start(db) if get_settings().run_workers else []
    yield
    await workers.stop(tasks)
    dbmod.close()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="Way Out API", version=VERSION, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in s.cors_origins.split(",")],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for module in ROUTERS:
        app.include_router(module.router)
    return app


app = create_app()
