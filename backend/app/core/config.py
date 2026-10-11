from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ARC Raiders Inventory Optimizer"
    database_url: str = "postgresql+asyncpg://arc:arc@localhost:5432/arc_optimizer"
    cors_origins: str = "http://localhost:4200,http://localhost"


    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
