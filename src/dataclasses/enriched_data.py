from dataclasses import dataclass

from src.dataclasses.news import News


@dataclass(kw_only=True)
class EnrichedData(News):
    entities: str
    sentiment: str
    sentiment_score: float
    categories: str
    keywords: str

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "id": self.id,
            "guidislink": self.guidislink,
            "published": self.published,
            "published_parsed": self.published_parsed,
            "summary": self.summary,
            "source": self.source,
            "sub_articles": self.sub_articles,
            "title_detail": self.title_detail,
            "links": self.links,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "entities": self.entities,
            "categories": self.categories,
            "keywords": self.keywords,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            link=data["link"],
            id=data["id"],
            guidislink=data["guidislink"],
            published=data["published"],
            published_parsed=data["published_parsed"],
            summary=data["summary"],
            source=data["source"],
            sub_articles=data["sub_articles"],
            title_detail=data["title_detail"],
            links=data["links"],
            sentiment=data["sentiment"],
            sentiment_score=data["sentiment_score"],
            entities=data["entities"],
            categories=data["categories"],
            keywords=data["keywords"],
        )

    @classmethod
    def from_news(cls, news: News):
        return cls(
            title=news.title,
            link=news.link,
            id=news.id,
            guidislink=news.guidislink,
            published=news.published,
            published_parsed=news.published_parsed,
            summary=news.summary,
            source=news.source,
            sub_articles=news.sub_articles,
            title_detail=news.title_detail,
            links=news.links,
            sentiment=None,
            sentiment_score=None,
            entities=None,
            categories=None,
            keywords=None,
        )
