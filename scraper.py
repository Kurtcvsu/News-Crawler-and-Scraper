import requests
import feedparser
from bs4 import BeautifulSoup
from typing import Dict, List, TypedDict, Literal, Tuple, Optional
from datetime import datetime, timedelta
import time

class Article(TypedDict):
    topic: str
    title: str
    link: str
    published: str
    body: str

Status = Literal["ok", "not-modified", "error"]

TOPIC_KEYWORDS = {
    "ai": ["artificial intelligence", "AI", "machine learning", "neural", "GPT", "model", "LLM", "deep learning", "transformer", "Philippines", "Llama", "Gemini", "Claude", "ChatGPT", "fine-tune", "RAG", "NAIS", "DOST AI"],
    "cybersecurity": ["cybersecurity", "security", "vulnerability", "breach", "malware", "exploit", "ransomware", "hacking", "cyber", "threat", "Philippines", "LockBit", "Conti", "Emotet", "Qakbot", "BlackCat", "zero-day", "APT", "Cobalt Strike", "CIRT", "DICT-CERT", "PNP-ACG"],
    "blockchain": ["blockchain", "crypto", "bitcoin", "ethereum", "Web3", "NFT", "decentralized", "smart contract", "Philippines", "BTC", "Solana", "zkSync", "Arbitrum", "Optimism", "Axie Infinity", "P2E", "BSP", "PDAX", "Coins.ph", "Maya crypto"]
}

def fetch_rss_items(feeds_dict: Dict[str, List[str]]) -> List[Dict]:
    """Fetch RSS feeds and filter articles by topic keywords."""
    items = []
    cutoff = datetime.now() - timedelta(hours=24)
    
    for topic, urls in feeds_dict.items():
        keywords = TOPIC_KEYWORDS.get(topic, [])
        
        for url in urls:
            try:
                print(f"Fetching feed: {url}")
                resp = requests.get(
                    url,
                    timeout=10,
                    headers={"User-Agent": "NewsDigestBot/1.0"},
                )
                resp.raise_for_status()

                feed = feedparser.parse(resp.content)
                
                for entry in feed.entries[:20]:
                    title = entry.get("title", "").lower()
                    summary = entry.get("summary", "").lower()
                    published_struct = entry.get("published_parsed")
                    if not published_struct:
                        continue #skip if no date

                    counter = sum(
                                int(keyword.lower() in title or keyword.lower() in summary) 
                                for keyword in keywords)

                    has_keyword = counter >= 2

                    date_released = datetime(*published_struct[:6])
                    
                    latest_date = date_released >= cutoff

                    if has_keyword and latest_date:
                        items.append({
                            "topic": topic,
                            "title": entry.get("title", ""),
                            "link": entry.get("link", ""),
                            "published": entry.get("published", ""),
                            "summary": entry.get("summary", "")
                        })
            
            except Exception as e:
                print(f"Error fetching {url}: {e}")
            
            time.sleep(0.5)
    
    return items

def extract_article_body(url: str, cached_last_modified: Optional[str] = None) -> Tuple[str, Status, Optional[str]]:
    """Fetch the full article page and extract the main text."""
    try:
        headers = {
            "User-Agent": "NewsDigestBot/1.0 (+https://github.com/Kurtcvsu/News-Crawler-and-Scraper)"
        }

        if cached_last_modified:
            headers["If-Modified-Since"] = cached_last_modified
        
        response = requests.get(url, timeout=10, headers=headers)

        if response.status_code == 304:
            return "", "not-modified", None

        response.raise_for_status()

        new_last_modified = response.headers.get("Last-Modified")
        
        soup = BeautifulSoup(response.text, "lxml")
        
        for tag in soup(["script", "style"]):
            tag.decompose()
        
        content = None
        for selector in ["article", "main", "[role='main']"]:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            content = soup.body if soup.body else soup
        
        text = content.get_text(separator=" ", strip=True)
        words = text.split()[:1500]
        return " ".join(words), "ok", new_last_modified
    
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return "", "error", None

def enrich_articles(items: List[Dict], url_cache: Dict[str, Dict[str, str]]) -> List[Article]:
    """Take articles from RSS and fetch their full text from the web."""
    enriched: List[Article] = []
    
    for item in items:
        url = item["link"]

        cached_for_url = url_cache.get(url, {})
        cached_last_modified = cached_for_url.get("last_modified")
        cached_body = cached_for_url.get("body", "")

        body, Status, new_last_modified = extract_article_body(url, cached_last_modified=cached_last_modified)

        if Status == "ok":
            if new_last_modified:
                url_cache[url] = {
                    "last_modified": new_last_modified,
                    "body": body
                }
        else:
            body = cached_body or item.get("summary", "")
        
        enriched.append(Article(
            topic=item["topic"],
            title=item["title"],
            link=item["link"],
            published=item["published"],
            body=body,
        ))
        
        time.sleep(0.5)
    
    return enriched
