"""Calls: the call floor reads (D1-04) and POST /calls/dial (D1-05)."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pymongo import DESCENDING

from api import requests as rq
from api.core.db import get_db
from api.routes._util import not_yet, out

router = APIRouter(prefix="/calls", tags=["calls"])

HOUSEHOLD_FIELDS = ("address", "simulated", "reach", "role", "record", "corrections", "language", "zoneId")


def _summary(call: dict[str, Any], hh: dict[str, Any] | None) -> dict[str, Any]:
    turns = call.get("turns") or []
    agent = call.get("agent") or {}
    last = turns[-1] if turns else {}
    return {
        "id": call["_id"],
        "householdId": call.get("householdId"),
        "direction": call.get("direction"),
        "language": call.get("language"),
        "startedAt": call.get("startedAt"),
        "endedAt": call.get("endedAt"),
        "updatedAt": call.get("updatedAt") or call.get("startedAt"),
        "outcome": call.get("outcome"),
        "stage": agent.get("stage"),
        "done": bool(agent.get("done")),
        "escalations": agent.get("escalations") or [],
        "turnCount": len(turns),
        "lastText": last.get("text"),
        "lastSpeaker": last.get("speaker"),
        "household": {"id": hh["_id"], **{k: hh.get(k) for k in HOUSEHOLD_FIELDS}} if hh else None,
    }


@router.get("")
async def list_calls(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    """Most recently active calls first, with a household summary. For the /calls list."""
    db = get_db()
    calls = [c async for c in db.calls.find({}).sort("updatedAt", DESCENDING).limit(limit)]
    ids = list({c.get("householdId") for c in calls})
    hhs = {h["_id"]: h async for h in db.households.find({"_id": {"$in": ids}})}
    return [_summary(c, hhs.get(c.get("householdId"))) for c in calls]


@router.get("/{call_id}")
async def get_call(call_id: str) -> dict:
    """One call: summary + every turn + the household's open request."""
    db = get_db()
    call = await db.calls.find_one({"_id": call_id})
    if call is None:
        raise HTTPException(404, "call not found")
    hh = await db.households.find_one({"_id": call.get("householdId")})
    req = await db.requests.find_one(
        {"householdId": call.get("householdId"), "status": {"$in": list(rq.OPEN_STATUSES)}}
    )
    return {**_summary(call, hh), "turns": call.get("turns") or [], "request": out(req)}


class DialBody(BaseModel):
    householdId: str


@router.post("/dial")
async def dial(body: DialBody) -> dict:
    """→ {callId}. Real call via Cartesia for real phones, stand-in for simulated homes."""
    raise not_yet("D1-05", "Deep")
