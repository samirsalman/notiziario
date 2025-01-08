from qdrant_client import QdrantClient

from src.knowledge.news_knowledge import QdrantNewsKnowledge

knowledge = QdrantNewsKnowledge(
    db=QdrantClient(host="localhost", port=6333),
    vector_dim=1024,
    embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    sparse_embedding_model_name="Qdrant/bm42-all-minilm-l6-v2-attentions",
)

while True:
    query = input("Query: ")
    results = knowledge.search(query, top_k=2)
    for result in results:
        print("Article", result.summary, "\n\n")
