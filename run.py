import logging
from datetime import timedelta

from qdrant_client import QdrantClient

from src.agents.agent import Country, PeriodicAgent
from src.knowledge.news_knowledge import QdrantNewsKnowledge

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    knowledge = QdrantNewsKnowledge(
        db=QdrantClient(host="db", port=6333),
        vector_dim=1024,
        embedding_model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        sparse_embedding_model_name="Qdrant/bm42-all-minilm-l6-v2-attentions",
    )
    agent = PeriodicAgent(
        period=timedelta(minutes=30),
        knowledge=knowledge,
        countries=[Country.ITALY, Country.USA],
        llm_model="gpt-4o-mini",
        max_per_country=10,
    )
    logging.info("Starting agent...")

    agent.run()
