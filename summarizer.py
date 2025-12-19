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

def summarize_articles(topic: str, articles: List[Dict], custom_prompt: str = None) -> str:
    """Use Gemini to create a summary of articles with customizable prompt."""
    if not articles:
        return f"No {topic} articles found."
    
    articles_text = "\n\n".join([
        f"Title: {a['title']}\nLink: {a['link']}\nBody: {a['body']}"
        for a in articles
    ])
    
    if custom_prompt:
        prompt = custom_prompt.format(topic=topic.upper(), articles=articles_text)
    else:
        return f"No custom prompt found for {topic}"
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini for summary: {e}")
        return f"Failed to summarize {topic} articles."





def generate_topic_summary(topic: str, articles: List[Dict], custom_prompt: str = None) -> str:
    """Generate a complete summary for a single topic using prompts_config.json."""
    if not articles:
        return f"No {topic} articles found today."
    
    init_gemini()
    
    # Load prompt from config file if no custom prompt provided
    if not custom_prompt:
        try:
            import json
            with open("prompts_config.json", "r", encoding="utf-8") as f:
                prompts_config = json.load(f)
            custom_prompt = prompts_config.get(topic, {}).get("prompt")
        except FileNotFoundError:
            print(f"prompts_config.json not found, using default for {topic}")
    
    print(f"Generating summary for {topic}...")
    summary = summarize_articles(topic, articles, custom_prompt)
    
    return summary

def generate_separate_summaries(articles_by_topic: Dict[str, List[Dict]], custom_prompts: Dict[str, str] = None) -> Dict[str, str]:
    """Generate separate summaries for each topic using prompts_config.json."""
    summaries = {}
    
    for topic in ["ai", "cybersecurity", "web3"]:
        if topic in articles_by_topic and articles_by_topic[topic]:
            summary = generate_topic_summary(topic, articles_by_topic[topic])
            summaries[topic] = summary
            
            filename = f"{topic}_summary.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"✅ {topic.upper()} summary saved to {filename}")
    
    return summaries


