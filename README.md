Coding Challenge - News Ingest Pipeline

This is a coding challenge for Isentia for a role I am applying for.

## The challenge:

### News Ingest Pipeline

#### Overview

This challenge will showcase the candidate's ability to integrate external APIs, manage dependencies, utilise cloud services (AWS Kinesis), and containerise an application using Docker. The task is to create a robust Python script that periodically fetches news articles from a public API and streams the structured data into an AWS Kinesis stream.

#### Scenario: Aurora Analytics

Aurora Analytics, a fast-growing media intelligence firm, relies heavily on real-time news and market sentiment data. The ability to quickly integrate new data sources is critical to the company’s success.

NewsAPI.org, a premium global news aggregator, has just provided Aurora Analytics with API access to their comprehensive feed. This is a critical opportunity to enrich Aurora's analytical models with high-fidelity, high-volume news data.

The immediate need is to build a modern, scalable, and resilient ingestion service. This service must securely connect to the NewsAPI feed, reliably process the incoming articles, and stream the raw, structured data onto a dedicated AWS Kinesis Data Stream for downstream processing by Aurora's machine learning and sentiment analysis engines. The content is a real-time stream, therefore the system should regularly pull content from the API and optimise to reduce latency when delivering to clients.

#### Core Requirements

1. API Integration: Fetch news data from the public Everything API from NewsAPI.
2. Data Processing: Structure and validate the retrieved data.
3. Kinesis Integration: Write the processed data to a configured AWS Kinesis Data Stream.
4. Containerization: Package the application and its dependencies using Docker.

#### Technical Requirements

The ingested article data written to Kinesis should be a JSON object containing at least the following fields (after being extracted and cleaned from the API response):

- `article_id` (Unique identifier)
- `source_name`
- `title`
- `content`
- `Url`
- `author`
- `published_at`
- `ingested_at`

#### Deliverables

The candidate should submit the URL of a public Git repository (e.g., GitHub, GitLab) containing at a minimum the following:

1. Python code - The main application logic
2. Dockerfile - An executable Docker container
3. README.md

## The Solution

A containerized script that occasionally fetches news from NewsAPI.org and sends the results to an AWS Kinesis Data Stream.

### Prerequisites

I have assumed an AWS account is already set up and configured.

1.  **NewsAPI Key**: Register at [NewsAPI.org](https://newsapi.orgregister).
2.  **AWS Kinesis Stream**: Create a stream using the AWS CLI:
    ```bash
    aws kinesis create-stream --stream-name news-stream --shard-count 1 --region ap-southeast-1
    ```
3.  **IAM Permissions**: Ensure the execution has this policy:
    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": ["kinesis:PutRecord", "kinesis:DescribeStreamSummary"],
          "Resource": "arn:aws:kinesis:ap-southeast-1:YOUR_ACCOUNT_ID:stream/news-stream"
        }
      ]
    }
    ```

### Configuration

Create a `.env` file in the project root with the following variables:

```env
NEWSAPI_KEY=<NewsAPI Key>
SEARCH_TERM=<NewsAPI search term>
PAGE_SIZE=100
AWS_REGION=ap-southeast-1
AWS_ACCESS_KEY_ID=<AWS Access Key>
AWS_SECRET_ACCESS_KEY=<AWS Secret Access Key>
```

Note: the SEARCH_TERM is injected directly in the q parameter of the API call, so it can follow the advances search syntax described in the [NewsAPI documentation](https://newsapi.org/docs/endpoints/search-articles).

### Docker Implementation

#### Build the Image

```bash
 docker build -t aurora-analytics-news-ingestor .
```

#### Run the Image

```bash
 docker run --rm --it --env-file .env --name app2 aurora-analytics-news-ingestor
```

### Development

#### Option 1: Use venv

```bash
python -m venv .venv
```

Windows PowerShell:

```
./.venv/Scripts/Activate.ps1
```

Windows (cmd):

```
./.venv/Scripts/activate.bat
```

macOs/Linux:

```
source .venv/bin/activate
```

Then install dependencies

```
pip3 install -r requirements.txt
```

#### Option 2: Using dev containers (VSCode)

1. Open the folder in VSCode
2. Run: _Dev Containers: Reopen in Container_
