from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.endpoints import router
from app.config.app import app_settings
from app.config.kafka import kafka_settings
from app.infra.logger import setup_logging
from app.infra.producer import KafkaProducer


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    kafka_producer = KafkaProducer(kafka_settings.bootstrap_servers)
    await kafka_producer.start()
    app.state.kafka_producer = kafka_producer

    yield

    await kafka_producer.stop()


app = FastAPI(
    title=app_settings.app_name,
    debug=app_settings.debug,
    lifespan=lifespan,
)
app.include_router(router)
