from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTConfig(BaseSettings):
    public_key: str = "not-so-secret"
    algorithm: str = "RS256"
    exp_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="jwt_",
        extra="ignore",
    )


jwt_settings = JWTConfig()
