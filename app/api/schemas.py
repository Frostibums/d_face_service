from uuid import UUID

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    event_id: UUID
    filename: str
    message: str
