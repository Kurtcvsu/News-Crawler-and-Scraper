import json
from scraper import fetch_rss_items, enrich_articles
import textwrap

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

    print("Grouping articles by topic")
    articles_by_topic: dict[str, list[dict]] = {}
    for article in enriched:
        topic = article["topic"]
        if topic not in articles_by_topic:
            articles_by_topic[topic] = []
        articles_by_topic[topic].append(article)

    # Open one file per topic
    topic_files = {
        "ai": open("ai_articles.txt", "w", encoding="utf-8"),
        "cybersecurity": open("cybersecurity_articles.txt", "w", encoding="utf-8"),
        "blockchain": open("blockchain_articles.txt", "w", encoding="utf-8"),
    }

    try:
        print("Saving articles to topic files...")
        
        for topic, f in topic_files.items():
            f.write(f"=== {topic.upper()} ===\n\n")

            for article in articles_by_topic.get(topic, []):   
                f.write(f"\"{article.upper(['title'])}\"\n")
                f.write(f"{article['published']}\n\n")
                
                wrapped_lines = textwrap.wrap(article['body'], width=100)
                f.write("\n")
                for line in wrapped_lines:
                    f.write(line + "\n")
                
                f.write(f"{article['link']}\n")
                f.write("\n" + "=" *80 + "\n\n")


        print("✅ Articles saved to ai_articles.txt, cybersecurity_articles.txt, blockchain_articles.txt")
    finally:
        # Make sure files are closed even if something crashes
        for f in topic_files.values():
            f.close()


if __name__ == "__main__":
    main()
