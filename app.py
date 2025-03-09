import configparser
import feedparser
import tweepy
import schedule
import time
import re

from llama_cpp import Llama

###############################################################################
# 1. LOAD CONFIG FROM config.ini
###############################################################################
config = configparser.ConfigParser()
config.read("config.ini")

# [Twitter] section
API_KEY = config["Twitter"]["API_KEY"]
API_KEY_SECRET = config["Twitter"]["API_KEY_SECRET"]
ACCESS_TOKEN = config["Twitter"]["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = config["Twitter"]["ACCESS_TOKEN_SECRET"]

# [Llama] section
LLAMA_MODEL_PATH = config["Llama"]["MODEL_PATH"]

# [Bot] section
WOEID = config["Bot"].get("WOEID", "23424977")  # default to USA if not found
QUERY = config["Bot"].get("QUERY", "AI OR #AI")
MAX_TWEETS = int(config["Bot"].get("MAX_TWEETS", 5))

# If you want to store RSS feed URLs or intervals here, you can:
# e.g. RSS_FEEDS = config["Bot"].get("RSS_FEEDS", "https://arxiv.org/rss/cs.AI").split(",")

# For demonstration, let's just use a couple static RSS feeds:
RSS_FEEDS = [
    "https://www.techradar.com/rss",
    "https://export.arxiv.org/rss/cs.AI",
]

# Adjust how many articles to fetch per feed
MAX_ARTICLES_PER_FEED = 3

# Post interval (in hours)
POST_INTERVAL_HOURS = 6


###############################################################################
# 2. AUTHENTICATE WITH TWITTER VIA V2 (FREE TIER)
###############################################################################
def authenticate_v2():
    """
    Create a Tweepy Client for Twitter's v2 API.
    Need 'Read and write' permission on the dev portal.
    """
    # NOTE: The Free tier now requires you also have a BEARER_TOKEN
    # If your config doesn't have one, add it.
    # e.g. BEARER_TOKEN = config["Twitter"]["BEARER_TOKEN"]
    # For this example, we'll just skip if we don't have it:
    bearer_token = config["Twitter"].get("BEARER_TOKEN", None)

    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        bearer_token=bearer_token
    )
    return client


###############################################################################
# 3. INITIALIZE LOCAL LLAMA
###############################################################################
llm = Llama(
    model_path=LLAMA_MODEL_PATH,
    n_ctx=2048,
    temperature=0.8,
    top_p=0.9,
    max_tokens=512  # more tokens for longer output
)


###############################################################################
# 4. PARSE RSS FEEDS (EXAMPLE: AI NEWS)
###############################################################################
def fetch_ai_news():
    """
    Fetch articles from each feed (up to MAX_ARTICLES_PER_FEED).
    Returns a list of dicts with title/link/summary.
    """
    articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url.strip())
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title = getattr(entry, "title", "No Title")
            link = getattr(entry, "link", "")
            summary = getattr(entry, "summary", "")
            articles.append({"title": title, "link": link, "summary": summary})
    return articles


###############################################################################
# 5. SUMMARIZE AN ARTICLE USING LLAMA
###############################################################################
def summarize_article(article):
    """
    Summarize the article into ~2 or 3 sentences using local Llama.
    """
    prompt_text = (
    "You are an AI assistant focusing on AI news. Summarize the following "
    "article in about 3 or 4 sentences. Provide key insights and context. "
    "Be concise and natural and creative:\n\n"
    f"Title: {article['title']}\n\n"
    f"Summary: {article['summary']}\n\n"
    "Multi-sentence Summary:"
)


    try:
        print("DEBUG - Prompt about to be sent:\n", prompt_text)

        response = llm(prompt=prompt_text)
        print(response)
        text_output = response["choices"][0]["text"].strip()

        # You can fine-tune this cleanup logic to your liking
        text_output = re.sub(r"\s+", " ", text_output)
        
        # If you want to ensure it stays under 280 characters (e.g., for tweets):
        if len(text_output) > 280:
            text_output = text_output[:279] + "…"
            
        return text_output
    except Exception as e:
        print(f"Llama Summarization Error: {e}")
        return article["title"]  # fallback


###############################################################################
# 6. COMPOSE FINAL TWEET (ADD HASHTAGS, ETC.)
###############################################################################
def compose_tweet(summary, link):
    """
    Combine the summary, link, and optional hashtags.
    """
    # Example hashtags
    hashtags = "#AI #TechNews"
    tweet = f"{summary}\nRead more: {link}\n{hashtags}"

    if len(tweet) > 280:
        tweet = tweet[:279] + "…"
    return tweet


###############################################################################
# 7. POST TWEET USING TWITTER V2
###############################################################################
def post_tweet_v2(client, tweet_text):
    """
    Post a tweet via v2. The Free tier has ~500 tweets/month limit.
    """
    try:
        response = client.create_tweet(text=tweet_text)
        tweet_id = response.data["id"]
        print(f"Tweet posted! ID: {tweet_id}")
    except tweepy.errors.Forbidden as e:
        print(f"Forbidden error (likely no write access or monthly limit): {e}")
    except tweepy.TweepyException as e:
        print(f"Other Tweepy error: {e}")


###############################################################################
# 8. MAIN BOT LOGIC
###############################################################################
def run_bot():
    client = authenticate_v2()

    # Fetch articles from RSS
    articles = fetch_ai_news()

    # Summarize and post tweets
    count = 0
    for article in articles:
        if count >= MAX_TWEETS:
            break
        summary = summarize_article(article)
        tweet_text = compose_tweet(summary, article["link"])
        post_tweet_v2(client, tweet_text)
        count += 1
        # Sleep briefly between tweets to avoid spamming
        time.sleep(5)


###############################################################################
# 9. SCHEDULE THE BOT
###############################################################################
def main():
    # Run the bot
    run_bot()

if __name__ == "__main__":
    main()

