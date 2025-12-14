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

    # Open one file per topic
    topic_files = {
        "ai": open("ai_articles.txt", "w", encoding="utf-8"),
        "cybersecurity": open("cybersecurity_articles.txt", "w", encoding="utf-8"),
        "blockchain": open("blockchain_articles.txt", "w", encoding="utf-8"),
    }

    try:
        print("Saving articles to topic files...")
        for article in enriched:
            topic = article["topic"]
            # Skip topics you don't handle
            if topic not in topic_files:
                continue

            f = topic_files[topic]
            f.write(f"=== {article['topic'].upper()} ===\n")
            f.write(f"Title: {article['title']}\n")
            f.write(f"Link: {article['link']}\n")
            f.write(f"Published: {article['published']}\n\n")
            f.write(article["body"])
            f.write("\n\n" + "=" * 80 + "\n\n")

        print("✅ Articles saved to ai_articles.txt, cybersecurity_articles.txt, blockchain_articles.txt")
    finally:
        # Make sure files are closed even if something crashes
        for f in topic_files.values():
            f.close()


if __name__ == "__main__":
    main()
