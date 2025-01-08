# Notiziario: News Enrichment Engine

Notiziario is a Python application designed to enrich news articles with additional information using Large Language Models (LLMs). It retrieves news articles periodically, cleans their summaries, extracts entities, sentiments, categories, and keywords using an LLM, and stores the enriched data in a knowledge base.

## Table of Contents

- [Notiziario: News Enrichment Engine](#notiziario-news-enrichment-engine)
  - [Table of Contents](#table-of-contents)
  - [Components](#components)
    - [Enrichers](#enrichers)
    - [Knowledge Base](#knowledge-base)
  - [Requirements](#requirements)
    - [Environment Variables](#environment-variables)
  - [Getting Started](#getting-started)
    - [Running Notiziario](#running-notiziario)
    - [Run with Docker](#run-with-docker)
  - [Future Work](#future-work)

## Components 

### Enrichers

Notiziario utilizes a modular enricher architecture. Currently, it supports the following enrichers that leverage an LLM:

*   **SummaryCleaner:** Cleans the article summary from HTML tags, special characters, and other noise.
*   **EntityEnricher:** Extracts entities (people, organizations, locations) from the summary.
*   **SentimentEnricher:** Analyzes the sentiment of the article (positive, neutral, negative) and assigns a score.
*   **CategoryEnricher:** Identifies the category (e.g., business, sports) of the article.
*   **KeywordEnricher:** Extracts keywords from the summary.

### Knowledge Base

Notiziario uses Qdrant as the knowledge base by default. You can configure a different knowledge base by implementing the `Knowledge` interface.

## Requirements

### Environment Variables

Notiziario uses environment variables for configuration. You can set the following variables:

- `OPENAI_API_KEY`: OpenAI API key for the LLM.

## Getting Started

### Running Notiziario

1.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2.  Create .env file with needed variables

3.  Run the script:

    ```bash
    python run.py
    ```

This will start the Notiziario agent, which will periodically retrieve news, enrich them, and store them in the knowledge base.

### Run with Docker

This project includes Docker support for easy deployment. You can build and run the containerized Notiziario with:

```bash
bash docker/build.sh <TAG_NAME>
```

You can then run the system with:

```bash
docker compose -f docker-compose.local.yaml up
```

## Future Work

- [ ] Implement search functionality using the knowledge base.
- [ ] Support additional news sources and languages.
- [ ] Integrate with different knowledge base solutions.
- [ ] Add unit and integration tests.
- [ ] Improve error handling and logging.
- [ ] Implement a web interface for browsing enriched news.
- [ ] Explore different LLMs and prompting strategies for better enrichment.
- [ ] Add monitoring and alerting capabilities.