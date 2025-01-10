from abc import ABC, abstractmethod
from typing import Any, List

from src.databases.database import Database
from src.dataclasses.aggregators import KeywordsAggregation, SentimentAggregation
from src.dataclasses.enriched_data import EnrichedData


class Aggregator(ABC):
    def __init__(self, database: Database):
        super().__init__()
        self.database = database

    @abstractmethod
    def run(self, *args, **kwargs):
        pass


class KeywordsAggregator(Aggregator):
    def __init__(self, database):
        super().__init__(database)

    def run(self, data: List[EnrichedData], metadata: dict, *args, **kwargs):
        keywords_aggregation = KeywordsAggregation.empty(metadata=metadata)

        for enriched_data in data:
            for keyword in enriched_data.keywords:
                keywords_aggregation.add_keyword(keyword)

        self.database.store(
            id=keywords_aggregation._id,
            data=keywords_aggregation.to_dict(),
            collection="keywords_aggregations",
        )
        return keywords_aggregation


class SentimentAggregator(Aggregator):
    def __init__(self, database):
        super().__init__(database)

    def run(self, data: List[EnrichedData], metadata: dict, *args, **kwargs):
        sentiment_aggregation = SentimentAggregation.empty(metadata=metadata)

        for enriched_data in data:
            sentiment_aggregation.add_sentiment(enriched_data.sentiment)

        self.database.store(
            id=sentiment_aggregation._id,
            data=sentiment_aggregation.to_dict(),
            collection="sentiment_aggregations",
        )
        return sentiment_aggregation


class AggregatorManager:
    def __init__(self):
        self.aggregators = {}

    def add_aggregator(self, aggregator: Aggregator):
        self.aggregators[aggregator.__class__.__name__] = aggregator

    def run(self, data: Any, metadata: dict, *args, **kwargs):
        for aggregator in self.aggregators.values():
            aggregator.run(data, metadata, *args, **kwargs)
        return True
