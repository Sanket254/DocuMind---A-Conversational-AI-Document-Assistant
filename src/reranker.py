from sentence_transformers import CrossEncoder


class Reranker:
    """
    Re-ranks retrieved documents using a CrossEncoder.
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        print(f"Loading reranker: {model_name}")
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5,
    ):
        """
        Returns the top_k most relevant documents.
        """

        if not documents:
            return []

        pairs = [
            (query, doc["content"])
            for doc in documents
        ]

        scores = self.model.predict(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        documents.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return documents[:top_k]