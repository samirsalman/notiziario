from datetime import datetime

from src.databases.database import Database
from src.dataclasses.aggregators import KeywordsAggregation, SentimentAggregation
from src.knowledge.knowledge import Knowledge


class QueryBuilder:
    def __init__(self, knowledge: Knowledge, database: Database):
        self.knowledge = knowledge
        self.database = database

    def run(
        self,
        country: str = "all",
        keyword: str = None,
        sentiment: str = None,
        limit: int = 10,
    ):
        query = {}
        if country != "all":
            query["country"] = country
        if keyword:
            query["keyword"] = keyword
        if sentiment:
            query["sentiment"] = sentiment

        return self.knowledge.retrieve(query, metadata={}, top_k=limit)

    def _aggregate_keywords(self, keywords: list[KeywordsAggregation]):
        aggregation = KeywordsAggregation.empty()

        for keyword_aggregation in keywords:
            for keyword, count in keyword_aggregation.keywords.items():
                aggregation.keywords[keyword] = (
                    aggregation.keywords.get(keyword, 0) + count
                )

        return aggregation

    def get_keywords(self, start_date: datetime, end_date: datetime, top_k: int = 10):
        query = {
            "date_time": {
                "$gte": start_date,
                "$lt": end_date,
            }
        }

        result = self.database.query(
            query=query,
            collection="keywords_aggregations",
        )

        return (
            self._aggregate_keywords(
                [KeywordsAggregation.from_dict(data) for data in result]
            )
            .sort(reverse=True)
            .limit(top_k)
        )

    def _aggregate_sentiments(self, sentiments: list[SentimentAggregation]):
        aggregation = SentimentAggregation.empty()

        for sentiment_aggregation in sentiments:
            for sentiment, count in sentiment_aggregation.sentiment.items():
                aggregation.sentiment[sentiment] = (
                    aggregation.sentiment.get(sentiment, 0) + count
                )

        return aggregation

    def get_sentiments(self, start_date: datetime, end_date: datetime, top_k: int = 10):
        query = {
            "date_time": {
                "$gte": start_date,
                "$lt": end_date,
            }
        }

        result = self.database.query(
            query=query,
            collection="sentiment_aggregations",
        )

        return (
            self._aggregate_sentiments(
                [SentimentAggregation.from_dict(data) for data in result]
            )
            .sort(reverse=True)
            .limit(top_k)
        )
