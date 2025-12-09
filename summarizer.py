import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def init_gemini():
    """Initialize the Gemini API client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")
    genai.configure(api_key=api_key)

def summarize_articles(topic: str, articles: List[Dict]) -> str:
    """Use Gemini to create a summary of articles."""
    if not articles:
        return f"No {topic} articles found."
    
    articles_text = "\n\n".join([
        f"Title: {a['title']}\nLink: {a['link']}\nBody: {a['body']}"
        for a in articles
    ])
    
    prompt = f"""You are a professional tech news summarizer. 
Read these {topic.upper()} articles and provide a concise summary.

Format your response as:
**SUMMARY:**
[3-4 sentences summarizing the main points]

Articles:
{articles_text}

SUMMARY:"""
    
    try:
        model = genai.GenerativeModel("gemini-flash-lite-latest")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini for summary: {e}")
        return f"Failed to summarize {topic} articles."

def generate_insights(topic: str, articles: List[Dict]) -> str:
    """Use Gemini to generate insights and key takeaways."""
    if not articles:
        return f"No {topic} articles found."
    
    articles_text = "\n\n".join([
        f"Title: {a['title']}\nLink: {a['link']}\nBody: {a['body']}"
        for a in articles
    ])
    
    prompt = f"""You are a tech industry analyst. 
Analyze these {topic.upper()} articles and extract KEY INSIGHTS and emerging TRENDS.

Format your response as:
**KEY INSIGHTS:**
- [Insight 1]
- [Insight 2]
- [Insight 3]

**EMERGING TRENDS:**
- [Trend 1]
- [Trend 2]

**WHY IT MATTERS:**
[2-3 sentences explaining the impact]

Articles:
{articles_text}

INSIGHTS AND TRENDS:"""
    
    try:
        model = genai.GenerativeModel("gemini-flash-lite-latest")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini for insights: {e}")
        return f"Failed to generate insights for {topic}."

def format_sources(articles: List[Dict]) -> str:
    """Format article sources as a numbered list."""
    if not articles:
        return "No sources found."
    
    sources = "**SOURCES:**\n"
    for i, article in enumerate(articles, start=1):
        sources += f"{i}. [{article['title']}]({article['link']})\n"
    
    return sources

def generate_daily_digest(articles_by_topic: Dict[str, List[Dict]]) -> str:
    """Create a complete daily digest with summary, insights, and sources."""
    init_gemini()
    
    digest = "📰 Daily Tech Digest\n"
    digest += "=" * 50 + "\n\n"
    
    for topic in ["ai", "cybersecurity", "blockchain"]:
        if topic in articles_by_topic and articles_by_topic[topic]:
            digest += f"\n🔹 {topic.upper()}\n"
            digest += "-" * 30 + "\n\n"
            
            print(f"Generating summary for {topic}...")
            summary = summarize_articles(topic, articles_by_topic[topic])
            digest += summary + "\n\n"
            
            print(f"Generating insights for {topic}...")
            insights = generate_insights(topic, articles_by_topic[topic])
            digest += insights + "\n\n"
            
            print(f"Formatting sources for {topic}...")
            sources = format_sources(articles_by_topic[topic])
            digest += sources + "\n\n"
    
    digest += "\n" + "=" * 50 + "\n"
    digest += "📌 Share your thoughts in the comments!\n"
    digest += "🔗 Follow for daily tech insights\n"
    
    return digest
