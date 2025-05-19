from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    bootstrap_servers: str = "kafka:29092"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="kafka_",
        extra="ignore",
    )


kafka_settings = KafkaConfig()
