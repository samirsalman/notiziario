from abc import abstractmethod
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    QueryResponse,
)

from src.dataclasses.enriched_data import EnrichedData
from src.knowledge.knowledge import Knowledge


class NewsKnowledge(Knowledge):
    def __init__(self, db):
        super().__init__(db)

    @abstractmethod
    def retrieve(
        self, query: str, metadata: dict, top_k=10, *args, **kwargs
    ) -> List[EnrichedData]:
        pass

    @abstractmethod
    def exists(self, id: str, metadata: dict | None = None, *args, **kwargs):
        return super().exists(id, metadata, *args, **kwargs)

    @abstractmethod
    def store(
        self, data: List[EnrichedData], metadata: List[dict], *args, **kwargs
    ) -> bool:
        pass

    @abstractmethod
    def update(self, data: EnrichedData, metadata: dict, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def delete(self, id: str, *args, **kwargs) -> bool:
        pass

    @abstractmethod
    def search(self, query: str, metadata: dict, *args, **kwargs) -> List[EnrichedData]:
        pass

    @abstractmethod
    def list(self, metadata: dict, *args, **kwargs) -> List[EnrichedData]:
        pass

    @abstractmethod
    def count(self, metadata: dict, *args, **kwargs) -> int:
        pass


class QdrantNewsKnowledge(NewsKnowledge):
    def __init__(
        self,
        db: QdrantClient,
        embedding_model_name: str,
        sparse_embedding_model_name: str,
        vector_dim: int = 1024,
    ):
        super().__init__(db)
        self.collection_name = "news_collection"
        self.embedding_model_name = embedding_model_name
        self.db: QdrantClient = db
        self.vector_dim = vector_dim

        # Set the embedding model
        self.db.set_model(embedding_model_name)
        self.db.set_sparse_model(sparse_embedding_model_name)

    def exists(self, id: str, metadata: dict | None = None, *args, **kwargs) -> bool:
        if not self.db.collection_exists(self.collection_name):
            return False
        if len(self.search("", metadata={"id": id}, top_k=1)):
            return True

        return False

    def retrieve(
        self, query: str, metadata: dict | None = None, top_k=10, *args, **kwargs
    ) -> List[EnrichedData]:
        if metadata is None:
            metadata = {}
        query_filter = self._build_filter(metadata)

        hits = self.db.query(
            collection_name=self.collection_name,
            query_text=query,
            query_filter=query_filter,
            limit=top_k,
        )

        return [self._convert_to_enriched_data(hit) for hit in hits]

    def store(
        self, data: List[EnrichedData], metadata: List[dict], *args, **kwargs
    ) -> bool:
        for doc in data:
            self.delete(doc.id)
        documents = [item.summary for item in data]
        combined_metadata = [
            {**item.to_dict(), **meta} for item, meta in zip(data, metadata)
        ]

        self.db.add(
            collection_name=self.collection_name,
            documents=documents,
            metadata=combined_metadata,
        )

        return True

    def update(self, data: EnrichedData, metadata: dict, *args, **kwargs) -> bool:
        # Update by storing the updated document (overwrite if ID exists)
        self.store([data], [metadata])
        return True

    def delete(self, id: str) -> bool:
        if not self.db.collection_exists(self.collection_name):
            return False

        result = self.db.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(must=[FieldCondition(key="id", match=MatchValue(value=id))])
            ),
        )

        return result is not None

    def search(
        self, query: str, metadata: dict | None = None, top_k=10, *args, **kwargs
    ) -> List[EnrichedData]:
        return self.retrieve(query, metadata, top_k=top_k, *args, **kwargs)

    def list(self, metadata: dict, *args, **kwargs) -> List[EnrichedData]:
        query_filter = self._build_filter(metadata)
        hits = self.db.scroll(
            collection_name=self.collection_name,
            query_filter=query_filter,
            limit=100,  # Fetch in batches
        )

        return [self._convert_to_enriched_data(hit) for hit in hits]

    def count(self, metadata: dict, *args, **kwargs) -> int:
        query_filter = self._build_filter(metadata)
        count = self.db.count(
            collection_name=self.collection_name, query_filter=query_filter
        )

        return count

    def _build_filter(self, metadata: dict) -> Filter:
        """Construct a Qdrant filter object based on metadata."""
        conditions = [
            FieldCondition(key=key, match=MatchValue(value=value))
            for key, value in metadata.items()
        ]

        return Filter(must=conditions)

    def _convert_to_enriched_data(self, hit: QueryResponse) -> EnrichedData:
        """Convert a Qdrant hit into an EnrichedData object."""
        return EnrichedData.from_dict(hit.metadata)
