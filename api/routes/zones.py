"""POST /zones/{id}/status: TinyFish webhook (Deep: D1-07). Bearer INTERNAL_TOKEN.

The write is done. The dialer should react to `status = set` through the `zones` change stream.
"""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api import audit
from api.core.auth import require_internal_token
from api.core.db import get_db
from api.core.util import utcnow
from api.routes._util import out

router = APIRouter(prefix="/zones", tags=["zones"])


class ZoneStatusBody(BaseModel):
    status: Literal["ready", "set", "go", "clear"]
    sourceUrl: str | None = None


@router.post("/{zone_id}/status", dependencies=[Depends(require_internal_token)])
async def zone_status(zone_id: str, body: ZoneStatusBody) -> dict:
    db = get_db()
    prev = await db.zones.find_one({"_id": zone_id})
    await db.zones.update_one(
        {"_id": zone_id},
        {
            "$set": {"status": body.status, "sourceUrl": body.sourceUrl, "source": "tinyfish", "updatedAt": utcnow()},
            "$setOnInsert": {"name": zone_id, "county": ""},
        },
        upsert=True,
    )
    before = prev.get("status") if prev else None
    if before != body.status:
        await audit.log(db, "zone_status", f"{before} → {body.status}", zoneId=zone_id)
    return out(await db.zones.find_one({"_id": zone_id}))
