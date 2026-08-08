from app.repositories.health_repository import HealthRepository


class HealthService:
    """Logica de negocio: traduce el estado crudo de la base de datos
    en el reporte de salud que expone la API."""

    def __init__(self, repository: HealthRepository):
        self._repository = repository

    async def check_health(self) -> dict:
        is_reachable = await self._repository.ping()

        if is_reachable:
            return {"status": "ok", "database": "connected"}
        return {"status": "degraded", "database": "disconnected"}
