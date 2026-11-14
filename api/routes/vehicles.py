"""GET /vehicles, POST /vehicles/{id}/position, POST /vehicles/{id}/safety (Yash: D2-05, D2-08)."""

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import audit
from api.core.db import get_db
from api.core.util import utcnow
from api.routes._util import out

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("")
async def list_vehicles() -> list[dict]:
    return [out(v) async for v in get_db().vehicles.find({})]


class PositionBody(BaseModel):
    lon: float
    lat: float
    heading: float = 0
    speedMps: float = 0


@router.post("/{vehicle_id}/position")
async def position(vehicle_id: str, body: PositionBody) -> dict:
    # TODO(D2-07): also append to Tiger Data `vehicle_positions`.
    res = await get_db().vehicles.update_one(
        {"_id": vehicle_id},
        {
            "$set": {
                "location": {"type": "Point", "coordinates": [body.lon, body.lat]},
                "heading": body.heading,
                "speedMps": body.speedMps,
                "lastSeenAt": utcnow(),
            }
        },
    )
    if not res.matched_count:
        raise HTTPException(404, "vehicle not found")
    return {"ok": True}


class SafetyBody(BaseModel):
    state: Literal["ok", "check", "man_down", "sos"]
    lon: float | None = None
    lat: float | None = None


@router.post("/{vehicle_id}/safety")
async def safety(vehicle_id: str, body: SafetyBody) -> dict:
    db = get_db()
    doc: dict[str, Any] = {"state": body.state, "at": utcnow()}
    if body.lon is not None and body.lat is not None:
        doc["location"] = {"type": "Point", "coordinates": [body.lon, body.lat]}
    res = await db.vehicles.update_one({"_id": vehicle_id}, {"$set": {"safety": doc}})
    if not res.matched_count:
        raise HTTPException(404, "vehicle not found")
    if body.state in ("man_down", "sos"):
        await audit.log(db, "driver_safety", body.state, vehicleId=vehicle_id)
    return {"ok": True}
