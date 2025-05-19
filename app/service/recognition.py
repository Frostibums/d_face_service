import logging
from asyncio import to_thread
from pathlib import Path
from uuid import UUID

import face_recognition
import numpy as np

from app.infra.producer import KafkaProducer
from app.infra.storage import LocalImageStorage

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    def __init__(
        self,
        producer: KafkaProducer,
        image_storage: LocalImageStorage,
    ):
        self.producer = producer
        self.image_storage = image_storage
        self._reference_encodings: dict[str, np.ndarray] = {}

    def _load_references(self):
        self._reference_encodings.clear()
        reference_images = self.image_storage.list_reference_images()
        for file_path in reference_images:
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                student_id = file_path.stem
                self._reference_encodings[student_id] = encodings[0]

    def _recognize_face(self, image_path: Path) -> list[str]:
        recognized = []
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return recognized

        for student_id, reference_encoding in self._reference_encodings.items():
            for encoding in encodings:
                match = face_recognition.compare_faces(
                    [reference_encoding], encoding, tolerance=0.6
                )[0]
                if match:
                    recognized.append(student_id)
                if len(encodings) == len(recognized):
                    return recognized
        return recognized

    async def recognize_faces_for_event(self, event_id: UUID) -> list[UUID] | None:
        logger.info(f"Starting recognition process for event: {str(event_id)}")
        images = self.image_storage.list_images(event_id)
        if not images:
            logger.info(f"No images found for event {event_id}")
            return None

        self._load_references()

        async def process_batch(batch: list[Path]) -> list[UUID]:
            recognized = []
            for image_path in batch:
                logger.info(f"Working on: {str(image_path)}")
                student_ids = await to_thread(self._recognize_face, image_path)
                logger.info(f"Students found for {str(image_path)}: {student_ids}")

                if student_ids:
                    for student_id in student_ids:
                        await self.producer.publish_student_recognized(
                            event_id=str(event_id),
                            student_id=str(student_id),
                        )
                    recognized.extend([UUID(student_id) for student_id in student_ids])
            return list(set(recognized))

        BATCH_SIZE = 10
        batches = [images[i:i + BATCH_SIZE] for i in range(0, len(images), BATCH_SIZE)]

        recognized_student_ids = set()
        for batch in batches:
            recognized_batch = await process_batch(batch)
            recognized_student_ids.update(recognized_batch)

        self.image_storage.clear_event_folder(event_id)
        return list(recognized_student_ids)
