from fastapi import APIRouter, Depends

from app.core.database import get_database
from app.repositories.health_repository import MongoHealthRepository
from app.services.health_service import HealthService

router = APIRouter()


def get_health_service() -> HealthService:
    repository = MongoHealthRepository(database=get_database())
    return HealthService(repository=repository)


@router.get("/health")
async def health(service: HealthService = Depends(get_health_service)) -> dict:
    return await service.check_health()
