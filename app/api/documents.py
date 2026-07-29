from fastapi import APIRouter
from app.dependencies import vector_store

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.get("")
def list_documents():

    results = vector_store.collection.get(
        include=["metadatas"]
    )

    files = {}

    for metadata in results["metadatas"]:
        filename = metadata.get("source_file")
        if filename is None:
            continue
        if filename not in files:
            files[filename] = 0

        files[filename] += 1

    response = []

    for i, (filename, chunks) in enumerate(files.items(), start=1):
        response.append(
            {
                "id": i,
                "filename": filename,
                "chunks": chunks,
            }
        )

    return response


import os
from fastapi import HTTPException

@router.delete("/{filename}")
def delete_document(filename: str):

    results = vector_store.collection.get(
        include=["metadatas"]
    )

    ids_to_delete = []
    for doc_id, metadata in zip(results["ids"], results["metadatas"]):
        if metadata.get("source_file") == filename:
            ids_to_delete.append(doc_id)

    if not ids_to_delete:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    vector_store.collection.delete(
        ids=ids_to_delete
    )

    pdf_path = os.path.join(
        "data",
        "pdf",
        filename
    )

    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return {
        "message": f"{filename} deleted successfully"
    }