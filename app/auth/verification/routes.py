from fastapi import APIRouter, Body

from app.auth.authentication.models import TokenPair

verification = APIRouter(prefix="/verification", tags=["Verification"])


@verification.post("/confirm")
async def confirm(code: int = Body(embed=True)) -> TokenPair:
    pass
