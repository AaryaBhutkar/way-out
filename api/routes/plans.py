"""POST /plans/solve, GET /plans/latest (Yash: D2-04)."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from api.core.db import get_db
from api.routes._util import not_yet, out

router = APIRouter(prefix="/plans", tags=["plans"])


class SolveBody(BaseModel):
    solver: Literal["greedy", "ortools"] = "greedy"


@router.post("/solve")
async def solve(body: SolveBody) -> dict:
    """Run api/dispatch/ once. Writes `plans` + `proposed` assignments."""
    raise not_yet("D2-04", "Yash")


@router.get("/latest")
async def latest() -> dict:
    db = get_db()
    plan = await db.plans.find_one(sort=[("version", -1)])
    if plan is None:
        return {"plan": None, "assignments": []}
    rows = db.assignments.find({"planVersion": plan["version"], "status": {"$in": ["proposed", "offered"]}})
    return {"plan": out(plan), "assignments": [out(a) async for a in rows]}
