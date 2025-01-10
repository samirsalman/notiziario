import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from time import sleep
from typing import List
from uuid import uuid4

import openai
from tqdm import tqdm

from src.aggregators.aggregator import Aggregator, AggregatorManager
from src.databases.database import Database
from src.dataclasses.news import News
from src.dataclasses.run import RunDetail, RunStatus
from src.enrichers.enricher import (
    CategoryEnricher,
    EnricherManager,
    EntityEnricher,
    KeywordEnricher,
    SentimentEnricher,
    SummaryCleaner,
)
from src.knowledge.knowledge import Knowledge

logger = logging.getLogger(__name__)


class Country(Enum):
    USA = "us::en"
    UK = "gb::en"
    ITALY = "it::it"
    GERMANY = "de::de"
    FRANCE = "fr::fr"
    SPAIN = "es::es"

    def name(self) -> str:
        return self.value.split("::")[0].upper()

    def language(self) -> str:
        return self.value.split("::")[1]


class Agent(ABC):
    def __init__(
        self, knowledge: Knowledge, database: Database, aggregators: list[Aggregator]
    ):
        super().__init__()
        self.knowledge = knowledge
        self.database = database
        self.aggregator_manager = AggregatorManager()
        for aggregator in aggregators:
            self.aggregator_manager.add_aggregator(aggregator)

    def _init_run(self):
        self._current_run = RunDetail(
            _id=uuid4().hex,
            agent_id=self.__class__.__name__,
            start_time=datetime.now(),
            end_time=None,
            retrieved_data_size=0,
        )

    def _finalize_run(self, error: Exception = None):
        self._current_run.end_time = datetime.now()
        if error:
            self._current_run.status = RunStatus.FAILURE
            self._current_run.message = str(error)
        else:
            self._current_run.status = RunStatus.SUCCESS

        return self._current_run

    @abstractmethod
    def run(self, *args, **kwargs) -> bool:
        pass


class PeriodicAgent(Agent):
    def __init__(
        self,
        period: timedelta,
        knowledge: Knowledge,
        database: Database,
        countries: List[Country],
        aggregators: List[Aggregator] = None,
        llm_model: str = "gpt-4o-mini",
        max_per_country: int = 1,
    ):
        super().__init__(knowledge, database, aggregators or [])
        self.period = period
        self.countries = countries
        self.enricher_manager = EnricherManager()
        self._openai_client = openai.OpenAI()
        self.llm_model = llm_model
        self.max_per_country = max_per_country

        self.enricher_manager = (
            self.enricher_manager.add_enricher(
                SummaryCleaner(openai_client=self.openai_client)
            )
            .add_enricher(EntityEnricher(openai_client=self.openai_client))
            .add_enricher(SentimentEnricher(openai_client=self.openai_client))
            .add_enricher(CategoryEnricher(openai_client=self.openai_client))
            .add_enricher(KeywordEnricher(openai_client=self.openai_client))
        )

    @property
    def openai_client(self):
        return self._openai_client

    def run(self) -> bool:
        from pygooglenews import GoogleNews

        # periodic ingestor logic here
        while True:
            self._init_run()
            error = None
            try:
                for country in self.countries:
                    total_country = 0
                    news_provider = GoogleNews(
                        country=country.name(), lang=country.language()
                    )
                    news = news_provider.top_news()["entries"]
                    news = [News.from_dict(article) for article in news]
                    enriched_news = []
                    for article in tqdm(
                        news, desc=f"Ingesting news from {country.name()}"
                    ):
                        if total_country >= self.max_per_country:
                            logger.info(
                                "Reached max article per country, skipping other articles"
                            )
                            break
                        if not self.knowledge.exists(
                            article.id,
                        ):
                            enriched = self.enricher_manager.enrich(
                                article, model_name=self.llm_model
                            )
                            enriched_news.append(enriched)
                            total_country += 1

                    self.knowledge.store(
                        enriched_news,
                        metadata=[{"country": country.name()} for _ in enriched_news],
                    )
                    self._current_run.retrieved_data_size += total_country
                    self.aggregator_manager.run(
                        enriched_news,
                        metadata={"country": country.name()},
                    )
            except Exception as e:
                error = e
                logger.error(e)

            run = self._finalize_run(error)
            self.database.store(id=run._id, data=run.to_dict(), collection="runs")

            sleep(self.period.total_seconds())
