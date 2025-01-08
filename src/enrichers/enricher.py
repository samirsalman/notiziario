import json
import logging
from abc import ABC, abstractmethod
from copy import deepcopy

from openai import OpenAI

from src.dataclasses.enriched_data import EnrichedData
from src.dataclasses.news import News

logger = logging.getLogger(__name__)


class Enricher(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _enrich(self, data: EnrichedData, *args, **kwargs) -> EnrichedData:
        pass

    def _retry_if_json_error(self, data: EnrichedData, *args, **kwargs) -> EnrichedData:
        for _ in range(5):
            try:
                enriched = self._enrich(data, *args, **kwargs)
                return enriched
            except json.JSONDecodeError:
                logger.warning(
                    f"Error enriching data: {data} with enricher: {self}. Retrying..."
                )
                continue
        return None

    def enrich(self, data: News | EnrichedData, *args, **kwargs) -> EnrichedData:
        if not isinstance(data, EnrichedData):
            data = EnrichedData.from_news(data)

        logger.info(f"Enriching data: {data} with enricher: {self}")
        try:
            enriched = self._retry_if_json_error(data, *args, **kwargs)
            logger.info(f"Done with enricher: {self}")
            return enriched
        except Exception as e:
            logger.error(f"Error enriching data: {data} with enricher: {self}")
            logger.error(e)
            return None


class OpenAIEnricher(Enricher):
    def __init__(self, openai_client: OpenAI):
        super().__init__()
        self.openai_client = openai_client
        if not self.openai_client:
            self.openai_client = OpenAI()

    @abstractmethod
    def prompt(self, data: EnrichedData, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def _enrich(
        self, data: EnrichedData, model_name: str, *args, **kwargs
    ) -> EnrichedData:
        return super()._enrich(data, *args, **kwargs)

    def enrich(self, data: News | EnrichedData, model_name: str, *args, **kwargs):
        return super().enrich(data, model_name, *args, **kwargs)


class SummaryCleaner(OpenAIEnricher):
    def __init__(self, openai_client: OpenAI):
        super().__init__(openai_client)

    def prompt(self, data: EnrichedData) -> str:
        return f"""
        The following is a news article about {data.title}.

        Clean the summary of the article from HTML tags, special characters, and other noise.
        Return the cleaned summary using the following JSON format:
        {{
            "summary": "cleaned summary"
        }}
        No other comments or introduction are needed. Answer with the JSON only.
        """

    def _enrich(self, data: EnrichedData, model_name: str) -> EnrichedData:
        out = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": self.prompt(data)},
                {"role": "user", "content": data.summary},
            ],
        )

        parsed_out = json.loads(out.choices[0].message.content)
        data.summary = parsed_out["summary"]
        return data


class EntityEnricher(OpenAIEnricher):
    def __init__(self, openai_client: OpenAI):
        super().__init__(openai_client)

    def prompt(self, data: EnrichedData) -> str:
        return f"""
        The following is a news article about {data.title}.

        Extract the entities like people, organizations, locations, ecc...
        Return the entities using the following JSON format:
        {{
            "entities": [
                "entity1",
                "entity2",
                "entity3"
            ]
        }}
        No other comments or introduction are needed. Answer with the JSON only.
        """

    def _enrich(self, data: EnrichedData, model_name: str) -> EnrichedData:
        out = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": self.prompt(data)},
                {"role": "user", "content": data.summary},
            ],
        )

        parsed_out = json.loads(out.choices[0].message.content)
        data.entities = sorted(list(set([e for e in parsed_out["entities"]])))
        return data


class SentimentEnricher(OpenAIEnricher):
    def __init__(self, openai_client: OpenAI):
        super().__init__(openai_client)

    def prompt(self, data: EnrichedData) -> str:
        return f"""
        The following is a news article about {data.title}.

        Extract the sentiment of the article using a scale from 0 to 5,
        Return the sentiment using the following JSON format:
        {{
            "sentiment": "positive" | "neutral" | "negative",
            "sentiment_score": 2.5 (float)
        }}
        No other comments or introduction are needed. Answer with the JSON only.
        """

    def _enrich(self, data: EnrichedData, model_name: str) -> EnrichedData:
        out = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": self.prompt(data)},
                {"role": "user", "content": data.summary},
            ],
        )

        parsed_out = json.loads(out.choices[0].message.content)
        data.sentiment = parsed_out["sentiment"]
        data.sentiment_score = parsed_out["sentiment_score"]
        return data


class CategoryEnricher(OpenAIEnricher):
    def __init__(self, openai_client: OpenAI):
        super().__init__(openai_client)

    def prompt(self, data: EnrichedData) -> str:
        return f"""
        The following is a news article about {data.title}.

        Extract the categories of the article,
        Return the categories using the following JSON format:
        {{
            "categories": [
                "category1",
                "category2",
                "category3"
            ]
        }}
        No other comments or introduction are needed. Answer with the JSON only.
        """

    def _enrich(self, data: EnrichedData, model_name: str) -> EnrichedData:
        out = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": self.prompt(data)},
                {"role": "user", "content": data.summary},
            ],
        )

        parsed_out = json.loads(out.choices[0].message.content)
        data.categories = sorted(list(set([e.lower() for e in parsed_out["categories"]])))
        return data


class KeywordEnricher(OpenAIEnricher):
    def __init__(self, openai_client: OpenAI):
        super().__init__(openai_client)

    def prompt(self, data: EnrichedData) -> str:
        return f"""
        The following is a news article about {data.title}.

        Extract the keywords of the article,
        Return the keywords using the following JSON format:
        {{
            "keywords": [
                "keyword1",
                "keyword2",
                "keyword3"
            ]
        }}
        No other comments or introduction are needed. Answer with the JSON only.
        """

    def _enrich(self, data: EnrichedData, model_name: str) -> EnrichedData:
        out = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": self.prompt(data)},
                {"role": "user", "content": data.summary},
            ],
        )

        parsed_out = json.loads(out.choices[0].message.content)
        data.keywords = sorted(list(set([e for e in parsed_out["keywords"]])))
        return data


class EnricherManager:
    def __init__(self):
        self.enrichers = []

    def add_enricher(self, enricher: Enricher) -> "EnricherManager":
        self.enrichers.append(enricher)
        return self

    def enrich(self, data: News | EnrichedData, *args, **kwargs) -> EnrichedData:
        enriched_data = deepcopy(data)
        for enricher in self.enrichers:
            enriched_data = enricher.enrich(enriched_data, *args, **kwargs)
            if not enriched_data:
                return None
        return enriched_data
