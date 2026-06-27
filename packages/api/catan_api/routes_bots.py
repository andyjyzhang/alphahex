from __future__ import annotations

from fastapi import APIRouter

from catan_bots import available_bots

router = APIRouter()


@router.get("/bots")
def bots() -> dict:
    return {"bots": available_bots()}
