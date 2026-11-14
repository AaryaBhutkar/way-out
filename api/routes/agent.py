"""POST /agent/start, POST /agent/turn (Deep: D1-02, D1-03, D1-04). Bearer INTERNAL_TOKEN."""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.agent import session
from api.core.auth import require_internal_token
from api.core.db import get_db

router = APIRouter(prefix="/agent", tags=["agent"], dependencies=[Depends(require_internal_token)])


class StartBody(BaseModel):
    householdId: str
    callType: Literal["outbound", "callback", "inbound"]
    callId: str


class TurnBody(BaseModel):
    callId: str
    householdId: str
    text: str = Field(max_length=2000)
    language: Literal["en", "es"] = "en"


@router.post("/start")
async def agent_start(body: StartBody) -> dict:
    """→ {say: [str], stage}"""
    return await session.start(get_db(), body.householdId, body.callType, body.callId)


@router.post("/turn")
async def agent_turn(body: TurnBody) -> dict:
    """→ {say: [str], stage, done, record, requestStatus}

    interpreter (api/agent/interpreter.py) → state machine (flow.py) → templates.py → honesty.py
    """
    return await session.turn(get_db(), body.callId, body.householdId, body.text, body.language)
