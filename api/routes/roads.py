"""POST /roads/closures (Dev 2: D2-06)."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from api import audit
from api.core.db import get_db
from api.core.util import new_id, utcnow
from api.models import LineString
from api.routes._util import out

router = APIRouter(prefix="/roads", tags=["roads"])


class ClosureBody(BaseModel):
    geometry: LineString
    source: Literal["hazard", "manual", "sim"] = "manual"


@router.post("/closures")
async def add_closure(body: ClosureBody) -> dict:
    """Stores the closure. TODO(D2-06): drop graph edges, re-plan now, revoke unreachable pickups
    with api.assignments.revoke() (only that pickup; the rest of the run stays frozen)."""
    db = get_db()
    doc = {"_id": new_id("rc"), "geometry": body.geometry.model_dump(), "source": body.source, "at": utcnow()}
    await db.roadClosures.insert_one(doc)
    await audit.log(db, "road_closed", body.source, closureId=doc["_id"])
    return out(doc)
