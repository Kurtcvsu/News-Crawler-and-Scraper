import requests
import feedparser
from bs4 import BeautifulSoup
from typing import Dict, List, TypedDict
from datetime import datetime, timedelta
import time

class Article(TypedDict):
    topic: str
    title: str
    link: str
    published: str
    body: str

TOPIC_KEYWORDS = {
    "ai": ["artificial intelligence", "AI", "machine learning", "neural", "GPT", "model", "LLM", "deep learning", "transformer", "Philippines", "Llama", "Gemini", "Claude", "ChatGPT", "fine-tune", "RAG", "NAIS", "DOST AI"],
    "cybersecurity": ["cybersecurity", "security", "vulnerability", "breach", "malware", "exploit", "ransomware", "hacking", "cyber", "threat", "Philippines", "LockBit", "Conti", "Emotet", "Qakbot", "BlackCat", "zero-day", "APT", "Cobalt Strike", "CIRT", "DICT-CERT", "PNP-ACG"],
    "blockchain": ["blockchain", "crypto", "bitcoin", "ethereum", "Web3", "NFT", "decentralized", "smart contract", "Philippines", "BTC", "Solana", "zkSync", "Arbitrum", "Optimism", "Axie Infinity", "P2E", "BSP", "PDAX", "Coins.ph", "Maya crypto"]
}

def fetch_rss_items(feeds_dict: Dict[str, List[str]]) -> List[Dict]:
    """Fetch RSS feeds and filter articles by topic keywords."""
    items = []
    
    for topic, urls in feeds_dict.items():
        keywords = TOPIC_KEYWORDS.get(topic, [])
        
        for url in urls:
            try:
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:20]:
                    title = entry.get("title", "").lower()
                    summary = entry.get("summary", "").lower()
                    published_date =  entry.get("published", "").lower()
                    
                    counter = sum(
                                int(keyword.lower() in title or keyword.lower() in summary) 
                                for keyword in keywords)

                    has_keyword = counter >= 2
                    
                    date_released = datetime.strptime(published_date, "%Y=%m-%d")
                    cutoff = datetime.now() - timedelta(days=7)
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

def extract_article_body(url: str) -> str:
    """Fetch the full article page and extract the main text."""
    try:
        headers = {
            "User-Agent": "NewsDigestBot/1.0 (+https://github.com/Kurtcvsu/News-Crawler-and-Scraper)"
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
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
        words = text.split()[:500]
        return " ".join(words)
    
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return ""

def enrich_articles(items: List[Dict]) -> List[Article]:
    """Take articles from RSS and fetch their full text from the web."""
    enriched = []
    
    for item in items:
        body = extract_article_body(item["link"])
        
        enriched.append(Article(
            topic=item["topic"],
            title=item["title"],
            link=item["link"],
            published=item["published"],
            body=body if body else item.get("summary", "")
        ))
        
        time.sleep(0.5)
    
    return enriched
