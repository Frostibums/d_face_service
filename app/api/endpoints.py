import logging
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, BackgroundTasks
from starlette import status

from app.api.dependencies import get_recognition_service, get_storage
from app.api.schemas import ImageUploadResponse
from app.infra.storage import LocalImageStorage
from app.service.recognition import FaceRecognitionService

router = APIRouter()


@router.post(
    "/images/upload/{event_id}",
    response_model=ImageUploadResponse,
)
async def upload_image(
        event_id: UUID,
        file: UploadFile = File(...),
        storage: LocalImageStorage = Depends(get_storage),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    content = await file.read()
    filename = f"{str(uuid.uuid4())}.jpg"

    storage.save(event_id, filename, content)

    return ImageUploadResponse(
        event_id=event_id,
        filename=filename,
        message="Image uploaded successfully."
    )


@router.post(
    "/recognition/{event_id}",
    response_model=None,
    status_code=status.HTTP_202_ACCEPTED,
)
async def complete_recognition(
        event_id: UUID,
        background_tasks: BackgroundTasks,
        service: FaceRecognitionService = Depends(get_recognition_service),
):
    background_tasks.add_task(service.recognize_faces_for_event, event_id=event_id)

