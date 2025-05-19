from pathlib import Path

from fastapi import Depends
from starlette.requests import Request

from app.infra.producer import KafkaProducer
from app.infra.storage import LocalImageStorage
from app.service.recognition import FaceRecognitionService


def get_storage() -> LocalImageStorage:
    return LocalImageStorage(base_path=Path("captured"))


def get_producer(request: Request) -> KafkaProducer:
    return request.app.state.kafka_producer


def get_recognition_service(
        producer: KafkaProducer = Depends(get_producer),
) -> FaceRecognitionService:
    return FaceRecognitionService(
        reference_dir=Path("references"),
        captured_dir=Path("captured"),
        kafka_producer=producer,
    )
