import os
import requests
import time
from pydantic import BaseModel, Field, ValidationError
import uuid
from datetime import datetime, timezone
from typing import Any
import boto3

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = os.getenv("NEWSAPI_BASE", "https://newsapi.org/v2/everything")
API_FETCH_INTERVAL = int(os.getenv("API_FETCH_INTERVAL", 120))

KINESIS_STREAM_NAME = os.getenv("KINESIS_STREAM_NAME", "news-stream")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")

kinesis_client = boto3.client("kinesis", region_name=AWS_REGION)
session = requests.Session()


class Article(BaseModel): 
    article_id: str = Field(default_factory=lambda: str(uuid.uuid4().hex))
    source_name : str
    title: str | None = None
    content: str | None = None
    Url: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def validate_article(article: dict[str, Any]) ->  Article | None:
    try:

        return Article(
            source_name=article.get("source", {}).get("name", "Unknown Source"),
            title=article.get('title' ),
            content=article.get('content'),
            Url=article.get('url'),
            author=article.get('author'),
            published_at=article.get('publishedAt')
        )

    except ValidationError as err:
        print(f"Validation error: {err.json()}")
        return None


def send_to_kinesis(article: Article):
    try:
        data = article.model_dump_json()
        kinesis_client.put_record(
            StreamName=KINESIS_STREAM_NAME,
            Data=data,
            PartitionKey=article.article_id,
        )
    except Exception as err:
        print(f"Failed to write to AWS Kinesis: {err}")

    
def fetch_news(q = "technology", page_size=20) -> list[Article]:
    print(f"[{datetime.now(timezone.utc)}] Fetching news for query: {q}")
    response = session.get(NEWSAPI_URL, params={
        "q": q,
        "apiKey": NEWSAPI_KEY,
        "pageSize": page_size,
    })
    response.raise_for_status()
    articles = response.json().get("articles", [])

    validated_list = []

    for a in articles:
        obj = validate_article(a)
        if (obj):
            validated_list.append(obj)
    return validated_list


def main(): 
    if not NEWSAPI_KEY: 
        print("NEWSAPI_KEY is not set")
        return



    while True:
        try: 
            articles = fetch_news()
            if articles:
                for article in articles: 
                    send_to_kinesis(article)
            print(f"Successfully processed {len(articles)} articles")
            time.sleep(API_FETCH_INTERVAL)
        except Exception as err: 
            print(f"Error: {err}")
            time.sleep(10)


if __name__ == "__main__": 
    main()
