from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion centralizada de la aplicacion, leida de variables de entorno."""

    model_config = SettingsConfigDict(env_file=".env")

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "proyecto_buttini"


settings = Settings()
