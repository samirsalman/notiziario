from dataclasses import dataclass


@dataclass
class Source:
    href: str
    title: str


@dataclass
class SubArticle:
    url: str
    title: str
    publisher: str


@dataclass
class TitleDetail:
    type: str


@dataclass
class Link:
    rel: str
    type: str
    href: str


@dataclass
class News:
    title: str
    link: str
    id: str
    guidislink: bool
    published: str
    published_parsed: list
    summary: str
    source: Source
    sub_articles: list[SubArticle]
    title_detail: TitleDetail
    links: list[Link]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data["title"],
            link=data["link"],
            id=data["id"],
            guidislink=data["guidislink"],
            published=data["published"],
            published_parsed=data["published_parsed"],
            summary=data["summary"],
            source=Source(href=data["source"]["href"], title=data["source"]["title"]),
            sub_articles=[
                SubArticle(
                    url=article["url"],
                    title=article["title"],
                    publisher=article["publisher"],
                )
                for article in data["sub_articles"]
            ],
            title_detail=TitleDetail(type=data["title_detail"]["type"]),
            links=[
                Link(rel=link["rel"], type=link["type"], href=link["href"])
                for link in data["links"]
            ],
        )

    def to_dict(self):
        return {
            "title": self.title,
            "link": self.link,
            "id": self.id,
            "guidislink": self.guidislink,
            "published": self.published,
            "published_parsed": self.published_parsed,
            "summary": self.summary,
            "source": {"href": self.source.href, "title": self.source.title},
            "sub_articles": [
                {
                    "url": article.url,
                    "title": article.title,
                    "publisher": article.publisher,
                }
                for article in self.sub_articles
            ],
            "title_detail": {"type": self.title_detail.type},
            "links": [
                {"rel": link.rel, "type": link.type, "href": link.href}
                for link in self.links
            ],
        }

    def __str__(self):
        return self.title
