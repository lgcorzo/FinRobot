# Reddit Adapter Stories

This document describes the Reddit adapter for social sentiment analysis from financial subreddits.

## Overview

The Reddit Adapter connects to the Reddit API to fetch posts and comments from financial subreddits for social sentiment analysis.

## Location

```
src/finrobot/data_access/data_source/
├── domains/social/
│   └── reddit_adapter.py    # DDD-style Reddit adapter
└── reddit_utils.py          # Reddit utility functions
```

## Key Functions

```python
from finrobot.data_access.data_source.reddit_utils import RedditUtils

reddit = RedditUtils()

# Get posts from subreddit
posts = reddit.get_subreddit_posts(
    subreddit="wallstreetbets",
    limit=100,
    time_filter="week"
)

# Search for ticker mentions
mentions = reddit.search_ticker_mentions(
    ticker="AAPL",
    subreddits=["stocks", "investing", "wallstreetbets"],
    limit=50
)

# Get comments on a post
comments = reddit.get_post_comments(post_id="abc123")
```

## Tracked Subreddits

| Subreddit        | Focus                    |
| ---------------- | ------------------------ |
| r/wallstreetbets | Retail trading sentiment |
| r/stocks         | General stock discussion |
| r/investing      | Long-term investing      |
| r/options        | Options trading          |
| r/stockmarket    | Market analysis          |

## Environment Variables

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

## Sentiment Analysis

Reddit data is typically processed for sentiment:

```python
# Fetch mentions
mentions = reddit.search_ticker_mentions("GME", limit=100)

# Analyze sentiment (via agent or NLP)
sentiment_scores = []
for mention in mentions:
    score = agent.analyze_sentiment(mention["text"])
    sentiment_scores.append(score)

# Aggregate sentiment
avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
```

## Rate Limiting

The Reddit API has rate limits. The adapter handles these automatically with exponential backoff.
