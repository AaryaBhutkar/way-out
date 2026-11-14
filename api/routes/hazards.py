"""GET /hazards, POST /hazards/photo (Dev 2: D2-07, P2 photo reports)."""

from fastapi import APIRouter

from api.core.db import get_db
from api.routes._util import not_yet, out

router = APIRouter(prefix="/hazards", tags=["hazards"])


@router.get("")
async def list_hazards() -> dict:
    """TODO(D2-07): add the fire front and per-home deadlines from api/hazard/spread.py."""
    db = get_db()
    return {
        "hazards": [out(h) async for h in db.hazards.find({})],
        "closures": [out(c) async for c in db.roadClosures.find({})],
    }


@router.post("/photo")
async def photo() -> dict:
    """multipart image + lon/lat → Gemini vision → hazard."""
    raise not_yet("P2 photo reports", "Dev 2")
