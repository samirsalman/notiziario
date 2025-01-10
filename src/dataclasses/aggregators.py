from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class KeywordsAggregation:
    _id: str
    date_time: datetime
    keywords: dict[str, int]
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            "_id": self._id,
            "date_time": self.date_time,
            "keywords": self.keywords,
            "metadata": self.metadata,
        }

    @classmethod
    def empty(cls, date_time: datetime = None, metadata: dict = None):
        return cls(
            _id=uuid4().hex,
            date_time=date_time or datetime.now(),
            keywords={},
            metadata=metadata or {},
        )

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data["_id"],
            date_time=data["date_time"],
            keywords=data["keywords"],
            metadata=data["metadata"],
        )

    def add_keyword(self, keyword: str):
        if keyword not in self.keywords:
            self.keywords[keyword] = 0
        self.keywords[keyword] += 1
        return self.keywords[keyword]

    def remove_keyword(self, keyword: str):
        if keyword in self.keywords:
            self.keywords[keyword] -= 1
            if self.keywords[keyword] == 0:
                del self.keywords[keyword]
            return self.keywords[keyword]
        return 0

    def get_keyword_count(self, keyword: str):
        return self.keywords.get(keyword, 0)

    def get_keywords(self):
        return list(self.keywords.keys())

    def limit(self, top_k: int):
        self.keywords = dict(
            sorted(self.keywords.items(), key=lambda x: x[1], reverse=True)[:top_k]
        )
        return self

    def sort(self, reverse: bool):
        self.keywords = dict(
            sorted(self.keywords.items(), key=lambda x: x[1], reverse=reverse)
        )
        return self


@dataclass
class SentimentAggregation:
    _id: str
    date_time: datetime
    sentiment: dict[str, int]
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        return {
            "_id": self._id,
            "date_time": self.date_time,
            "sentiment": self.sentiment,
            "metadata": self.metadata,
        }

    @classmethod
    def empty(cls, date_time: datetime = None, metadata: dict = None):
        return cls(
            _id=uuid4().hex,
            date_time=date_time or datetime.now(),
            sentiment={},
            metadata=metadata or {},
        )

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data["_id"],
            date_time=data["date_time"],
            sentiment=data["sentiment"],
            metadata=data["metadata"],
        )

    def add_sentiment(self, sentiment: str):
        if sentiment not in self.sentiment:
            self.sentiment[sentiment] = 0
        self.sentiment[sentiment] += 1
        return self.sentiment[sentiment]

    def remove_sentiment(self, sentiment: str):
        if sentiment in self.sentiment:
            self.sentiment[sentiment] -= 1
            if self.sentiment[sentiment] == 0:
                del self.sentiment[sentiment]
            return self.sentiment[sentiment]
        return 0

    def get_sentiment_count(self, sentiment: str):
        return self.sentiment.get(sentiment, 0)

    def get_sentiments(self):
        return list(self.sentiment.keys())

    def limit(self, top_k: int):
        self.sentiment = dict(
            sorted(self.sentiment.items(), key=lambda x: x[1], reverse=True)[:top_k]
        )
        return self

    def sort(self, reverse: bool):
        self.sentiment = dict(
            sorted(self.sentiment.items(), key=lambda x: x[1], reverse=reverse)
        )
        return self
