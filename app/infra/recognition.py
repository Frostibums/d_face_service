import logging
from pathlib import Path
from uuid import UUID

import face_recognition

logger = logging.getLogger(__name__)


class FaceRecognitionEngine:
    def __init__(self, ethalon_dir: Path):
        self.ethalon_dir = ethalon_dir
        self.ethalon_encodings: dict[UUID, list[float]] = {}
        self._load_ethalons()

    def _load_ethalons(self):
        for file in self.ethalon_dir.iterdir():
            if file.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
                continue
            try:
                student_id = UUID(file.stem)
                image = face_recognition.load_image_file(file)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.ethalon_encodings[student_id] = encodings[0]
            except Exception as e:
                logger.error(f"Ошибка при загрузке эталона {file.name}: {e}")

    def recognize(self, image_path: Path) -> UUID | None:
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if not encodings:
                return None
            captured_encoding = encodings[0]

            for student_id, eth_encoding in self.ethalon_encodings.items():
                matches = face_recognition.compare_faces(
                    [eth_encoding],
                    captured_encoding,
                    tolerance=0.6,
                )
                if matches[0]:
                    return student_id
        except Exception as e:
            logger.error(f"Ошибка при распознавании {image_path.name}: {e}")
        return None
