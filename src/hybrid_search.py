from rank_bm25 import BM25Okapi
from typing import Any


class HybridSearch:

    def __init__(self, vector_store, retriever, reranker):

        self.vector_store = vector_store
        self.retriever = retriever
        self.reranker = reranker

        self.bm25 = None
        self.documents = []

        self.build_index()

    ####################################################

    def build_index(self):

        data = self.vector_store.get_all_documents()

        docs = data["documents"]
        metas = data["metadatas"]
        ids = data["ids"]

        self.documents = []

        tokenized = []

        for doc, meta, doc_id in zip(docs, metas, ids):

            self.documents.append(
                {
                    "id": doc_id,
                    "content": doc,
                    "metadata": meta,
                    "file_name": meta.get("source_file"),
                    "page": meta.get("page"),
                }
            )

            tokenized.append(
                doc.lower().split()
            )

        self.bm25 = BM25Okapi(tokenized)

        print(f"BM25 indexed {len(self.documents)} chunks.")

    ####################################################

    def keyword_search(
    self,
    query,
    top_k=10,
    allowed_files=None,
):

        tokens = query.lower().split()

        if allowed_files:

            filtered_docs = []

            filtered_tokens = []

            for doc in self.documents:

                if doc["file_name"] in allowed_files:

                    filtered_docs.append(doc)

                    filtered_tokens.append(
                        doc["content"].lower().split()
                    )

            bm25 = BM25Okapi(filtered_tokens)

            scores = bm25.get_scores(tokens)

            ranked = sorted(
                zip(filtered_docs, scores),
                key=lambda x: x[1],
                reverse=True,
            )

        else:

            scores = self.bm25.get_scores(tokens)

            ranked = sorted(
                zip(self.documents, scores),
                key=lambda x: x[1],
                reverse=True,
            )

        return [
            doc
            for doc, score in ranked[:top_k]
        ]
    ####################################################

    def reciprocal_rank_fusion(
        self,
        dense,
        sparse,
        k=60,
    ):

        fused = {}

        # Dense results
        for rank, doc in enumerate(dense):

            doc_id = doc["id"]

            if doc_id not in fused:
                fused[doc_id] = {
                    "doc": doc,
                    "score": 0.0,
                }

            fused[doc_id]["score"] += 1 / (k + rank + 1)

        # BM25 results
        for rank, doc in enumerate(sparse):

            doc_id = doc["id"]

            if doc_id not in fused:
                fused[doc_id] = {
                    "doc": doc,
                    "score": 0.0,
                }

            fused[doc_id]["score"] += 1 / (k + rank + 1)

        ranked = sorted(
            fused.values(),
            key=lambda x: x["score"],
            reverse=True,
        )

        return [
            item["doc"]
            for item in ranked
        ]
    ####################################################

    def search(
    self,
    query,
    top_k=10,
    allowed_files=None,
    ):

        dense = self.retriever.dense_search(
            query=query,
            top_k=top_k,
            allowed_files=allowed_files,
        )

        sparse = self.keyword_search(
            query=query,
            top_k=top_k,
            allowed_files=allowed_files,
        )

        fused = self.reciprocal_rank_fusion(
            dense=dense,
            sparse=sparse,
        )

        reranked = self.reranker.rerank(
            query=query,
            documents=fused,
            top_k=top_k,
        )

        return reranked

    def refresh_index(self):
        """
        Rebuild BM25 after new documents are uploaded.
        """
        print("Refreshing BM25 index...")
        self.build_index()