from fastapi import APIRouter, Body

from app.auth.authentication.models import TokenPair
from app.auth.database.types import PyObjectId

verification = APIRouter(prefix="/verification", tags=["Verification"])


@verification.post("/confirm/{verification_id}")
async def confirm(verification_id: PyObjectId, code: str = Body(embed=True)) -> TokenPair:
    pass
