from typing import Protocol

from motor.motor_asyncio import AsyncIOMotorDatabase


class HealthRepository(Protocol):
    """Contrato de acceso a datos para el chequeo de salud.

    services/ depende de esta abstraccion, no de Mongo directamente (DIP).
    """

    async def ping(self) -> bool: ...


class MongoHealthRepository:
    """Implementacion concreta de HealthRepository sobre MongoDB."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self._database = database

    async def ping(self) -> bool:
        try:
            await self._database.command("ping")
            return True
        except Exception:
            return False
