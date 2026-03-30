from typing import Annotated, Any, Union
from pydantic import (
    PostgresDsn,
    BeforeValidator,
    computed_field,
    Field
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

def parse_cors_origins(v: Any) -> list[str]:
    """Zet een komma-gescheiden string om naar een lijst."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return v
    return []

# We gebruiken 'Any' in de Annotated om Pydantic niet te laten struikelen 
# over de initiële string-waarde uit de .env
CorsOrigins = Annotated[Any, BeforeValidator(parse_cors_origins)]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project & Security
    PROJECT_NAME: str = "FastAPI Project"
    # Gebruik openssh-genereerde sleutels voor productie, maar hier is een voorbeeld van een veilige sleutel voor ontwikkelingsdoeleinden
    SECRET_KEY: str = Field(..., min_length=32)

    # CORS - We gebruiken Union om zowel een lege lijst als de gevalideerde lijst toe te staan
    BACKEND_CORS_ORIGINS: CorsOrigins = []

    # Database velden... (zoals eerder besproken)
    # Deze komen uit je .env
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    
    # AI Model Configuratie
    AI_MODEL: str = "filipstrand/Z-Image-Turbo-mflux-4bit"
    LORA_PATH: str = "/Volumes/FloepieJoepie/ai/civitai/"
    LORA_PATHS: list[str] = []
    LORA_SCALES: list[float] = []

    # Celery instellingen
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    PYTHONPATH: str = "./src"

    # Templates en statische bestanden
    BASE_DIR: Path = Path(__file__).resolve().parent
    TEMPLATE_DIR: str = str(BASE_DIR / "templates")
    STATIC_DIR: str = str(BASE_DIR / "static")
    
    # Storage
    STORAGE_TYPE: str = "local"  # of 's3', 'gcs', etc.
    STORAGE_DIR: str = str(BASE_DIR / "storage")

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Stelt de URI samen: postgresql://user:pass@server:port/db"""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )
settings = Settings()