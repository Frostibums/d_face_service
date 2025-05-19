from pathlib import Path

from fastapi import Depends
from starlette.requests import Request

from app.infra.producer import KafkaProducer
from app.infra.storage import LocalImageStorage
from app.service.recognition import FaceRecognitionService


def get_producer(request: Request) -> KafkaProducer:
    return request.app.state.kafka_producer


def get_image_storage() -> LocalImageStorage:
    return LocalImageStorage(
        captured_path=Path("captured"),
        ethalons_path=Path("references"),
    )


def get_recognition_service(
        producer: KafkaProducer = Depends(get_producer),
        image_storage: LocalImageStorage = Depends(get_image_storage),
) -> FaceRecognitionService:
    return FaceRecognitionService(
        producer=producer,
        image_storage=image_storage,
    )
