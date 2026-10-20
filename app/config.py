import os
from dataclasses import dataclass


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    admin_password: str
    require_admin_auth: bool
    log_level: str


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("SHOPFLOW_DATABASE_URL", "sqlite:///./shopflow.db"),
        secret_key=os.getenv("SHOPFLOW_SECRET_KEY", "local-development-secret-change-me"),
        admin_password=os.getenv("SHOPFLOW_ADMIN_PASSWORD", "admin-demo-password"),
        require_admin_auth=_as_bool(os.getenv("SHOPFLOW_REQUIRE_ADMIN_AUTH", "true")),
        log_level=os.getenv("SHOPFLOW_LOG_LEVEL", "INFO").upper(),
    )


settings = get_settings()
