"""The callback queue: phone calls we owe a resident because their ride status changed.

Core rules only. The worker that actually places the calls is `api/agent/callbacks.py` (Deep, D1-06):
it picks up `state: queued` documents and marks them `placed → played | unanswered`.

`key = requestId:assignmentId:announcedStatus` has a unique index, so enqueueing twice is a no-op.
Approval NEVER triggers a callback (CONTRACT §1). Only the statuses below do.
"""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from api import audit
from api.core.util import new_id, utcnow

# en_route only when the ETA moved by more than 3 minutes; the caller decides that.
ANNOUNCED_STATUSES = frozenset({"driver_accepted", "reassigning", "en_route", "arrived"})


def callback_key(request_id: str, assignment_id: str, status: str) -> str:
    return f"{request_id}:{assignment_id}:{status}"


async def enqueue(db: AsyncIOMotorDatabase, request_id: str, assignment_id: str, status: str) -> dict[str, Any] | None:
    """Queue a callback. Returns the new doc, or None if this exact callback was already queued."""
    if status not in ANNOUNCED_STATUSES:
        raise ValueError(f"status {status!r} never triggers a callback")

    key = callback_key(request_id, assignment_id, status)
    doc = {
        "_id": new_id("cb"),
        "requestId": request_id,
        "assignmentId": assignment_id,
        "announcedStatus": status,
        "state": "queued",
        "key": key,
        "createdAt": utcnow(),
    }
    try:
        await db.callbacks.insert_one(doc)
    except DuplicateKeyError:
        await audit.log(db, "duplicate_callback_ignored", key, requestId=request_id, assignmentId=assignment_id)
        return None
    await audit.log(db, "callback_queued", key, requestId=request_id, assignmentId=assignment_id)
    return doc
