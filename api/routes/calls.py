"""POST /calls/dial (Deep: D1-05)."""

from fastapi import APIRouter
from pydantic import BaseModel

from api.routes._util import not_yet

router = APIRouter(prefix="/calls", tags=["calls"])


class DialBody(BaseModel):
    householdId: str


@router.post("/dial")
async def dial(body: DialBody) -> dict:
    """→ {callId}. Real call via Cartesia for real phones, stand-in for simulated homes."""
    raise not_yet("D1-05", "Deep")
