"""RED: definimos el contrato HTTP del endpoint /health antes de implementarlo."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.health import get_health_service
from app.services.health_service import HealthService


class FakeHealthRepository:
    def __init__(self, is_reachable: bool):
        self._is_reachable = is_reachable

    async def ping(self) -> bool:
        return self._is_reachable


@pytest.mark.asyncio
async def test_health_endpoint_returns_200_and_ok_status():
    app.dependency_overrides[get_health_service] = lambda: HealthService(
        repository=FakeHealthRepository(is_reachable=True)
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
