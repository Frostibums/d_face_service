from pydantic_settings import BaseSettings


class LoggerConfig(BaseSettings):
    level: str = "INFO"
    use_json: bool = False


logger_settings = LoggerConfig()
