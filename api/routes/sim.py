"""POST /sim/seed, POST /sim/control (Yash: D2-02). Everything from here is labeled SIM in the UI."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api.routes._util import not_yet

router = APIRouter(prefix="/sim", tags=["sim"])


@router.post("/seed")
async def seed(scenario: str = Query(default="pocket-fire")) -> dict:
    """Seeds ~200 homes, 8 vehicles, 2 shelters for the scenario."""
    raise not_yet("D2-02", "Yash")


class SimControl(BaseModel):
    standIns: dict[str, bool]  # {voice, drivers, approval}


@router.post("/control")
async def control(body: SimControl) -> dict:
    raise not_yet("D2-02", "Yash")
