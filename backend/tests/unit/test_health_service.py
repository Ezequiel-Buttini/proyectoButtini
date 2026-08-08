"""RED: definimos el comportamiento esperado de HealthService antes de escribirlo.

HealthService depende de una abstraccion de repositorio (no de Mongo
directamente), asi que en el test la reemplazamos por un fake liviano.
"""
import pytest

from app.services.health_service import HealthService


class FakeHealthRepository:
    def __init__(self, is_reachable: bool):
        self._is_reachable = is_reachable

    async def ping(self) -> bool:
        return self._is_reachable


@pytest.mark.asyncio
async def test_check_health_reports_ok_when_database_is_reachable():
    service = HealthService(repository=FakeHealthRepository(is_reachable=True))

    result = await service.check_health()

    assert result == {"status": "ok", "database": "connected"}


@pytest.mark.asyncio
async def test_check_health_reports_degraded_when_database_is_unreachable():
    service = HealthService(repository=FakeHealthRepository(is_reachable=False))

    result = await service.check_health()

    assert result == {"status": "degraded", "database": "disconnected"}
