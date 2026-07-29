from src.embedding_manager import EmbeddingManager
from src.vector_store import VectorStore
from src.retriever import RAGRetriever
from src.rag_pipeline import RAGPipeline
from src.llm import get_llm
from src.reranker import Reranker
from src.document_router import DocumentRouter
from src.hybrid_search import HybridSearch

from database import SessionLocal


print("Loading embedding model...")
embedding_manager = EmbeddingManager()


print("Loading vector database...")
vector_store = VectorStore()

print("Loading LLM...")
llm = get_llm()

print("Loading reranker...")
reranker = Reranker()

print("Loading document router...")
document_router = DocumentRouter(llm)



print("Creating retriever...")
retriever = RAGRetriever(
    vector_store=vector_store,
    embedding_manager=embedding_manager,
)

print("Creating hybrid search...")
hybrid_search = HybridSearch(
    vector_store=vector_store,
    retriever=retriever,
    reranker=reranker
)

print("Creating RAG pipeline...")
rag = RAGPipeline(
    llm=llm,
    document_router=document_router,
    vector_store=vector_store,
    hybrid_search=hybrid_search,
)



print("Backend initialized successfully.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()