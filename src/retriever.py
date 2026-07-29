from typing import List, Dict, Any

from src.vector_store import VectorStore
from src.embedding_manager import EmbeddingManager

class RAGRetriever:
    """Handles query-based retrieval from the vector store"""
    
    def __init__(self, vector_store: VectorStore, embedding_manager: EmbeddingManager,):
        """
        Initialize the retriever
        
        Args:
            vector_store: Vector store containing document embeddings
            embedding_manager: Manager for generating query embeddings
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager

    def dense_search(
    self,
    query: str,
    top_k: int = 5,
    allowed_files: list[str] | None = None,
) -> List[Dict[str, Any]]:

        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        query_args = {
            "query_embeddings": [query_embedding.tolist()],
            "n_results": max(top_k * 3, 15),
        }

        if allowed_files:
            print(f"Searching only files: {allowed_files}")

            query_args["where"] = {
                "source_file": {
                    "$in": allowed_files
                }
            }

        results = self.vector_store.collection.query(**query_args)

        retrieved_docs = []
        seen = set()

        if results["documents"] and results["documents"][0]:

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            ids = results["ids"][0]

            for doc_id, document, metadata, distance in zip(
                ids,
                documents,
                metadatas,
                distances,
            ):

                key = (
                    metadata.get("source_file"),
                    metadata.get("page"),
                    document[:100],
                )

                if key in seen:
                    continue

                seen.add(key)

                retrieved_docs.append(
                    {
                        "id": doc_id,
                        "content": document,
                        "metadata": metadata,
                        "file_name": metadata.get("source_file"),
                        "page": metadata.get("page"),
                        "distance": distance,
                    }
                )

        return retrieved_docs
