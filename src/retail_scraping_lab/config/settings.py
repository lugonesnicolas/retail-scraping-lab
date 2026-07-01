from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion de la aplicacion, cargada desde variables de entorno / .env."""

    model_config = SettingsConfigDict(env_prefix="RSL_", env_file=".env", extra="ignore")

    log_level: str = "INFO"

    http_timeout_seconds: float = 10.0
    http_user_agent: str = (
        "retail-scraping-lab/0.1 (+https://github.com/<usuario>/retail-scraping-lab)"
    )

    database_url: str = "sqlite:///./data/processed/retail_scraping_lab.db"

    data_raw_dir: Path = Path("data/raw")
    data_processed_dir: Path = Path("data/processed")
    data_exports_dir: Path = Path("data/exports")


def get_settings() -> Settings:
    return Settings()
