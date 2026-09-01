from pathlib import Path
import shutil

from fastapi import APIRouter, File, UploadFile
from app.services.document_service import ingest


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
def upload(file: UploadFile = File(...)):
    save_path = UPLOAD_DIR / (file.filename or "upload.txt")
    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return ingest(save_path)
