from fastapi import APIRouter, Body

from app.auth.authentication.tokens.models import TokenPair
from app.auth.database.types import PyObjectId
from app.auth.verification.services import confirm_verification

verification = APIRouter(prefix="/verification", tags=["Verification"])


@verification.post("/confirm/{verification_id}")
async def confirm(verification_id: PyObjectId, code: str = Body(embed=True)) -> TokenPair:
    return await confirm_verification(verification_id, code)
