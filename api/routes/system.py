"""GET /system/metrics (Deep: D1-09)."""

from fastapi import APIRouter

from api.routes._util import not_yet

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/metrics")
async def metrics() -> dict:
    """→ latency p50/p95, honesty, accuracy, dispatch results (data/sim-results.json)."""
    raise not_yet("D1-09", "Deep")
