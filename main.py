import os
import requests
import time
from pydantic import BaseModel, Field, ValidationError
import uuid
from datetime import datetime
from typing import Any

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = os.getenv("NEWSAPI_BASE", "https://newsapi.org/v2/everything")
API_FETCH_INTERVAL = int(os.getenv("API_FETCH_INTERVAL", 120))


class Article(BaseModel): 
    article_id: str = Field(default_factory=lambda: str(uuid.uuid4().hex))
    source_name : str
    title: str | None = None
    content: str | None = None
    Url: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    ingested_at: datetime = Field(default_factory=lambda: datetime.now())

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
    with open('log.txt', 'a') as f:
        f.write(article.model_dump_json())
        f.write('\n\n')

    
def fetch_news(q = "technology", page_size=20) -> list[Article]:
    print(f"Fetching news for query: {q}")
    session = requests.Session()
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
    while True:
        try: 
            articles = fetch_news()
            if articles:
                for article in articles: 
                    send_to_kinesis(article)
            print(f"Processed {len(articles)} articles")
            time.sleep(API_FETCH_INTERVAL)
        except Exception as err: 
            print(f"Error: {err}")


if __name__ == "__main__": 
    main()
