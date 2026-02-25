import os
import requests
import time
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWSAPI_URL = os.getenv("NEWSAPI_BASE", "https://newsapi.org/v2/everything")
API_FETCH_INTERVAL = int(os.getenv("API_FETCH_INTERVAL", 120))


class Article(BaseModel): 
    article_id: str = Field(default_factory=lambda: str(uuid.uuid4().hex))
    source_name : str
    title: str
    content: str
    Url: str
    author: str | None
    published_at: datetime 
    ingested_at: datetime

def validate_article(article: dict) ->  Article:
    return Article(
        source_name=article.get("source", {}).get("name"),
        title=article.get('title' ),
        content=article.get('content'),
        Url=article.get('url'),
        author=article.get('author'),
        published_at=article.get('publishedAt'),
        ingested_at=datetime.now().isoformat()
    )



def send_to_kinesis(article: Article):
    with open('log.txt', 'a') as f:
        f.write(article.model_dump_json())
        f.write('\n\n')

    
def fetch_news(q = "technology", page_size=20):
    try: 

        response = requests.get(NEWSAPI_URL, params={
            "q": q,
            "apiKey": NEWSAPI_KEY,
            "pageSize": page_size,
        })
        response.raise_for_status()
        return response.json().get("articles", [])

    except requests.exceptions.HTTPError as err: 
        print(f'An HTTP Error has occured: {err}')
    except requests.exceptions.RequestException as err:
        print(f'An error has occured: {err}')



def main(): 
    while True:
        try: 
            articles = fetch_news()
            # print(articles)
            for article in articles: 
                validated = validate_article(article=article)
                send_to_kinesis(validated)
            time.sleep(API_FETCH_INTERVAL)
        except Exception as err: 
            print(f"Error: {err}")


if __name__ == "__main__": 
    main()
