# AI News Twitter Bot

This is an AI-powered Twitter bot that fetches the latest AI-related news from RSS feeds, summarizes the content using a local Llama model, and posts tweets with links to the articles.

## Features
- Fetches AI news from predefined RSS feeds
- Summarizes articles using a locally hosted Llama model
- Composes tweets with relevant hashtags and article links
- Authenticates and posts tweets using Twitter API v2
- Schedules periodic posts automatically

## Requirements
### Dependencies
Ensure you have the following Python packages installed:
```bash
pip install configparser feedparser tweepy schedule llama-cpp-python
```

### Configuration
Create a `config.ini` file with the following structure:
```ini
[Twitter]
API_KEY = your_api_key
API_KEY_SECRET = your_api_key_secret
ACCESS_TOKEN = your_access_token
ACCESS_TOKEN_SECRET = your_access_token_secret
BEARER_TOKEN = your_bearer_token  # Required for free-tier authentication

[Llama]
MODEL_PATH = path_to_your_llama_model

[Bot]
WOEID = 23424977  # Default to USA
QUERY = AI OR #AI
MAX_TWEETS = 5
RSS_FEEDS = https://www.techradar.com/rss,https://export.arxiv.org/rss/cs.AI
POST_INTERVAL_HOURS = 6
```

## How It Works
1. **Authenticate with Twitter API**: Uses Tweepy to connect to Twitter and post tweets.
2. **Fetch AI News**: Pulls articles from RSS feeds.
3. **Summarize Articles**: Uses a local Llama model to generate concise summaries.
4. **Compose Tweets**: Adds hashtags and article links.
5. **Post Tweets**: Tweets are posted to Twitter through the API.
6. **Schedule Execution**: The bot runs at regular intervals (default: every 6 hours).

## Running the Bot
Run the bot manually:
```bash
python bot.py
```

Or schedule it using `schedule`:
```python
schedule.every(6).hours.do(run_bot)
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Notes
- Ensure your Twitter Developer account has the necessary permissions.
- The free-tier Twitter API has a limit on tweets per month.
- You may need to fine-tune the Llama model settings for better summaries.

## License
This project is licensed under the MIT License.
