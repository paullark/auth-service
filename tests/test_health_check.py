import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(app: AsyncClient) -> None:
    response = await app.get("/health-check")
    assert response.status_code == 204
