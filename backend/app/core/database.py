from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


def get_database() -> AsyncIOMotorDatabase:
    """Punto unico de acceso a la base de datos Mongo.

    Se crea un cliente por llamada a proposito: Motor maneja su propio pool
    de conexiones internamente, y esto evita que la app dependa de estado
    global mutable durante los tests.
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongo_uri)
    return client[settings.mongo_db_name]
