"""Offer lifecycle: approve → offered → accept (atomic) | decline | expire; accepted → revoke.

    proposed → offered → accepted → completed
    side exits: declined, expired, replaced (silent), revoked (resident is told)

Only one assignment per request is live (proposed/offered/accepted) at a time.
Request status moves go through api.requests.transition(), never directly.
"""

from datetime import datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from api import audit, callbacks
from api import requests as rq
from api.core.config import get_settings
from api.core.util import utcnow


class AssignmentError(Exception):
    def __init__(self, message: str, *, status_code: int = 409):
        super().__init__(message)
        self.status_code = status_code


async def _get(db: AsyncIOMotorDatabase, assignment_id: str) -> dict[str, Any]:
    a = await db.assignments.find_one({"_id": assignment_id})
    if a is None:
        raise AssignmentError(f"assignment {assignment_id} not found", status_code=404)
    return a


async def _has_live_offer(db: AsyncIOMotorDatabase, request_id: str) -> bool:
    return await db.assignments.count_documents({"requestId": request_id, "status": "offered"}) > 0


async def _settle_request_after_offer_closed(db: AsyncIOMotorDatabase, request_id: str, reason: str) -> None:
    """approved → received (silently) when no offer is left. A reassigning request stays reassigning."""
    req = await db.requests.find_one({"_id": request_id})
    if req and req["status"] == "approved" and not await _has_live_offer(db, request_id):
        await rq.transition(db, request_id, "received", reason=reason)


async def _vehicle_status(db: AsyncIOMotorDatabase, vehicle_id: str) -> None:
    """Derive the vehicle's status from its assignments."""
    if await db.assignments.count_documents({"vehicleId": vehicle_id, "status": "accepted"}):
        status = "on_run"
    elif await db.assignments.count_documents({"vehicleId": vehicle_id, "status": "offered"}):
        status = "offered"
    else:
        status = "idle"
    await db.vehicles.update_one({"_id": vehicle_id, "status": {"$ne": "offline"}}, {"$set": {"status": status}})


async def approve(db: AsyncIOMotorDatabase, assignment_id: str, *, by: str = "dispatcher") -> dict[str, Any]:
    """Dispatcher approves a proposed assignment. Approval is NOT a promise: no callback."""
    a = await _get(db, assignment_id)
    req = await db.requests.find_one({"_id": a["requestId"]})
    if req is None or req["status"] not in ("received", "approved", "reassigning"):
        raise AssignmentError(f"request is {req and req['status']}, can't offer it")

    now = utcnow()
    ttl = timedelta(seconds=get_settings().offer_ttl_seconds)
    offered = await db.assignments.find_one_and_update(
        {"_id": assignment_id, "status": "proposed"},
        {"$set": {"status": "offered", "offeredAt": now, "expiresAt": now + ttl}},
        return_document=ReturnDocument.AFTER,
    )
    if offered is None:
        raise AssignmentError(f"assignment is {a['status']}, not proposed")

    # One live assignment per request: anything else proposed/offered for it is replaced (silent).
    others = db.assignments.find(
        {"requestId": a["requestId"], "_id": {"$ne": assignment_id}, "status": {"$in": ["proposed", "offered"]}}
    )
    async for other in others:
        await db.assignments.update_one(
            {"_id": other["_id"], "status": other["status"]},
            {"$set": {"status": "replaced", "respondedAt": now}},
        )
        await _vehicle_status(db, other["vehicleId"])

    if req["status"] == "received":
        await rq.transition(db, a["requestId"], "approved", reason="dispatcher approved", by=by)

    await _vehicle_status(db, a["vehicleId"])
    await audit.log(db, "assignment_offered", "approved", assignmentId=assignment_id, by=by)
    return offered


async def accept(db: AsyncIOMotorDatabase, assignment_id: str, *, now: datetime | None = None) -> dict[str, Any]:
    """Driver taps Accept. Atomic: only an `offered`, unexpired assignment can be accepted.

    Returns {"result": "accepted", "assignment": ...} or {"result": "changed"}.
    """
    now = now or utcnow()
    won = await db.assignments.find_one_and_update(
        {"_id": assignment_id, "status": "offered", "expiresAt": {"$gt": now}},
        {"$set": {"status": "accepted", "respondedAt": now}},
        return_document=ReturnDocument.AFTER,
    )
    if won is None:
        await audit.log(db, "stale_accept_rejected", "assignment changed", assignmentId=assignment_id)
        return {"result": "changed"}

    try:
        await rq.transition(
            db,
            won["requestId"],
            "driver_accepted",
            reason="driver accepted",
            by=won["vehicleId"],
            allowed_from={"approved", "reassigning"},
        )
    except rq.RequestError:
        # The request moved under us (closed, etc.). Undo the accept so nothing is promised.
        await db.assignments.update_one({"_id": assignment_id}, {"$set": {"status": "replaced"}})
        await audit.log(db, "stale_accept_rejected", "request changed", assignmentId=assignment_id)
        return {"result": "changed"}

    await callbacks.enqueue(db, won["requestId"], assignment_id, "driver_accepted")
    await _vehicle_status(db, won["vehicleId"])
    return {"result": "accepted", "assignment": won}


async def decline(db: AsyncIOMotorDatabase, assignment_id: str) -> dict[str, Any]:
    now = utcnow()
    a = await db.assignments.find_one_and_update(
        {"_id": assignment_id, "status": "offered"},
        {"$set": {"status": "declined", "respondedAt": now}},
        return_document=ReturnDocument.AFTER,
    )
    if a is None:
        current = await _get(db, assignment_id)
        raise AssignmentError(f"assignment is {current['status']}, not offered")
    await _settle_request_after_offer_closed(db, a["requestId"], "driver declined")
    await _vehicle_status(db, a["vehicleId"])
    await audit.log(db, "assignment_declined", "declined", assignmentId=assignment_id)
    return a


async def revoke(db: AsyncIOMotorDatabase, assignment_id: str, *, reason: str) -> dict[str, Any]:
    """An accepted pickup can't happen (driver cancels / no route in time). The resident is told.

    Only this pickup is revoked; the driver's other accepted stops stay as they were.
    """
    now = utcnow()
    a = await db.assignments.find_one_and_update(
        {"_id": assignment_id, "status": "accepted"},
        {"$set": {"status": "revoked", "respondedAt": now}},
        return_document=ReturnDocument.AFTER,
    )
    if a is None:
        current = await _get(db, assignment_id)
        raise AssignmentError(f"assignment is {current['status']}, not accepted")

    await rq.transition(db, a["requestId"], "reassigning", reason=reason, allowed_from={"driver_accepted", "en_route"})
    await callbacks.enqueue(db, a["requestId"], assignment_id, "reassigning")
    await _vehicle_status(db, a["vehicleId"])
    await audit.log(db, "assignment_revoked", reason, assignmentId=assignment_id)
    return a


async def expire_offers(db: AsyncIOMotorDatabase, *, now: datetime | None = None) -> int:
    """Offers expire 2 minutes after offeredAt; the request goes silently back to received."""
    now = now or utcnow()
    n = 0
    async for a in db.assignments.find({"status": "offered", "expiresAt": {"$lte": now}}):
        res = await db.assignments.update_one(
            {"_id": a["_id"], "status": "offered"}, {"$set": {"status": "expired", "respondedAt": now}}
        )
        if res.modified_count:
            n += 1
            await _settle_request_after_offer_closed(db, a["requestId"], "offer expired")
            await _vehicle_status(db, a["vehicleId"])
            await audit.log(db, "assignment_expired", "expired", assignmentId=a["_id"])
    return n
