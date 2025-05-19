import shutil
from pathlib import Path
from uuid import UUID


class LocalImageStorage:
    def __init__(
            self,
            captured_path: Path,
            ethalons_path: Path,
    ):
        self.captured_path = captured_path
        self.ethalons_path = ethalons_path
        self.captured_path.mkdir(parents=True, exist_ok=True)

    def save(self, event_id: UUID, file_name: str, file_bytes: bytes) -> Path:
        event_dir = self.captured_path / str(event_id)
        event_dir.mkdir(parents=True, exist_ok=True)

        file_path = event_dir / file_name
        file_path.write_bytes(file_bytes)
        return file_path

    def list_images(self, event_id: UUID) -> list[Path]:
        image_extensions = {'.jpg', '.jpeg', '.png'}
        event_dir = self.captured_path / str(event_id)
        if not event_dir.exists():
            return []
        return [p for p in event_dir.iterdir() if p.suffix.lower() in image_extensions]

    def clear_event_folder(self, event_id: UUID) -> None:
        event_dir = self.captured_path / str(event_id)
        if event_dir.exists():
            shutil.rmtree(event_dir)

    def list_reference_images(self) -> list[Path]:
        return list(self.ethalons_path.glob("*.jpg"))
