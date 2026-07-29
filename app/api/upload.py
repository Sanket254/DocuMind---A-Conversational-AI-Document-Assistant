from fastapi import APIRouter, UploadFile, File, HTTPException

from pathlib import Path
import shutil

from ingest import ingest_pdf
from app.dependencies import (
    embedding_manager,
    vector_store,
    hybrid_search,
)

router = APIRouter(tags=["Upload"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    upload_dir = Path("data/pdf")
    upload_dir.mkdir(parents=True, exist_ok=True)

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_pdf(
        pdf_path=file_path,
        embedding_manager=embedding_manager,
        vector_store=vector_store,
    )
    hybrid_search.refresh_index()
    return result