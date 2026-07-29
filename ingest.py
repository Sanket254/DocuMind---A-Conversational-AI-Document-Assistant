from typing import Dict
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from src.text_splitter import split_documents


def ingest_pdf(pdf_path: str | Path, embedding_manager, vector_store,) -> Dict[str, int]:
    """
    Ingest a single PDF into the vector database.
    """

    pdf_path = Path(pdf_path)

    print(f"\nProcessing: {pdf_path.name}")

    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    # Add metadata
    for doc in documents:
        doc.metadata["source_file"] = pdf_path.name
        doc.metadata["file_type"] = "pdf"

    chunks = split_documents(documents)

    embeddings = embedding_manager.generate_embeddings(
        [doc.page_content for doc in chunks]
    )

    vector_store.add_documents(chunks, embeddings)

    return {
        "status": "success",
        "documents": len(documents),
        "chunks": len(chunks),
        "filename": pdf_path.name,
    }