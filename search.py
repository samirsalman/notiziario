from datetime import datetime

from qdrant_client import QdrantClient

from src.agents.agent import Country
from src.databases.database import MongoDatabase
from src.knowledge.news_knowledge import QdrantNewsKnowledge
from src.query.query_builder import QueryBuilder

knowledge = QdrantNewsKnowledge(
    db=QdrantClient(host="localhost", port=6333),
    vector_dim=1024,
    embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    sparse_embedding_model_name="Qdrant/bm42-all-minilm-l6-v2-attentions",
)

db = MongoDatabase(
    host="localhost",
    db_name="notiziario",
    username="root",
    password="example",
    port=27017,
)

# while True:
#     query = input("Query: ")
#     results = knowledge.search(query, top_k=2, metadata={"country": "IT"})
#     for result in results:
#         print("Article", result.summary, "\n\n")

query_builder = QueryBuilder(knowledge, db)


top_kw = query_builder.get_keywords(
    start_date=datetime(2025, 1, 1), end_date=datetime(2025, 1, 10), top_k=10
)


top_sentiments = query_builder.get_sentiments(
    start_date=datetime(2025, 1, 1), end_date=datetime(2025, 1, 10), top_k=10
)

print("### Top Keywords ###")
total_kw = sum(top_kw.keywords.values())
for keyword, count in top_kw.keywords.items():
    print(f"* {keyword}: {count} ({count / total_kw:.2%})")

print("\n### Top Sentiments ###")
total_sentiments = sum(top_sentiments.sentiment.values())
for sentiment, count in top_sentiments.sentiment.items():
    print(f"* {sentiment}: {count} ({count / total_sentiments:.2%})")
