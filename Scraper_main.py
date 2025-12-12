import json
from scraper import fetch_rss_items, enrich_articles

def main():
    """Main orchestration function."""
    print("Loading feeds from feeds.json...")
    with open("feeds.json", "r", encoding="utf-8") as f:
        feeds = json.load(f)

    print("Fetching RSS feeds...")
    raw_items = fetch_rss_items(feeds)
    print(f"Found {len(raw_items)} items from RSS")

    url_cache: dict[str, dict[str, str]] = {}

    print("Enriching articles with full text...")
    enriched = enrich_articles(raw_items, url_cache)

    print("Saving raw articles to output.txt...")
    with open("output.txt", "w", encoding="utf-8") as f:
        for article in enriched:
            f.write(f"=== {article['topic'].upper()} ===\n")
            f.write(f"Title: {article['title']}\n")
            f.write(f"Link: {article['link']}\n")
            f.write(f"Published: {article['published']}\n\n")
            f.write(article["body"])
            f.write("\n\n" + "=" * 80 + "\n\n")

    print("✅ Raw articles saved to output.txt")

if __name__ == "__main__":
    main()
