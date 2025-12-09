import json
from scraper import fetch_rss_items, enrich_articles
from summarizer import generate_daily_digest

def main():
    """Main orchestration function."""
    
    print("Loading feeds from feeds.json...")
    with open("feeds.json", "r") as f:
        feeds = json.load(f)
    
    print("Fetching RSS feeds...")
    raw_items = fetch_rss_items(feeds)
    print(f"Found {len(raw_items)} items from RSS")
    
    print("Enriching articles with full text...")
    enriched = enrich_articles(raw_items)
    
    print("Grouping articles by topic...")
    articles_by_topic = {}
    for article in enriched:
        topic = article["topic"]
        if topic not in articles_by_topic:
            articles_by_topic[topic] = []
        articles_by_topic[topic].append(article)
    
    print("Generating digest with Gemini...")
    digest = generate_daily_digest(articles_by_topic)
   
    print("Saving digest to output.txt...")
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(digest)

    print("✅ Digest saved to output.txt")
    print(digest)

if __name__ == "__main__":
    main()
