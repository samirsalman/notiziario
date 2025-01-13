from textwrap import fill
from datetime import datetime

from qdrant_client import QdrantClient

from src.agents.agent import Country
from src.databases.database import MongoDatabase
from src.knowledge.news_knowledge import QdrantNewsKnowledge
from src.query.query_builder import QueryBuilder

def choice(query, choices):
    for i in range(len(choices)):
        query += f" {i}. " + choices[i]

    while True:
        try:
            return choices[int(input(f"{query}: "))]
        except:
            pass


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

query_builder = QueryBuilder(knowledge, db)

top_kw = query_builder.get_keywords(
    start_date=datetime(2025, 1, 1), end_date=datetime.now(), top_k=10
)

top_sentiments = query_builder.get_sentiments(
    start_date=datetime(2025, 1, 1), end_date=datetime.now(), top_k=10
)


print("- Top Keywords")
total_kw = sum(top_kw.keywords.values())
for keyword, count in top_kw.keywords.items():
    print(f"* {count=:<3} ({100 * count / total_kw:>5.2f}%) - {keyword}")

print("\n- Top Sentiments")
total_sentiments = sum(top_sentiments.sentiment.values())
for sentiment, count in top_sentiments.sentiment.items():
    print(f"* {count=:<3} ({100 * count / total_sentiments:>5.2f}%) - {sentiment}")


print("\n- Search")
results = query_builder.run(
    query=input("Query: "),
    country=choice("Country", choices=[Country.ITALY.name(), Country.USA.name(), Country.FRANCE.name(), Country.SPAIN.name()]),
    sentiment=choice("Sentiment", choices=["positive", "negative", "neutral"]),
    limit=4
)

print()
for result in results:
    print(f"{'Title:':<10}", fill(result.title, width=128, subsequent_indent=' '*11))
    print(f"{'Summary:':<10}", fill(result.summary, width=128, subsequent_indent=' '*11))
    print(f"{'Sentiment:':<10}", result.sentiment)
    print(f"{'Keywords:':<10}", fill(str(result.keywords), width=128, subsequent_indent=' '*11))
    print("-" * 11)
