import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

import json

def init_gemini():
    """Initialize the Gemini API client."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")
    genai.configure(api_key=api_key)

def summarize_from_file(topic: str, custom_prompt: str = None) -> str:
    """Read articles from file and use Gemini to create a summary."""
    filename = f"{topic}_articles.txt"
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            articles_text = f.read()
    except FileNotFoundError:
        return f"No {filename} found."
    
    if not articles_text.strip():
        return f"No {topic} articles found in {filename}."
    
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

def generate_topic_summary(topic: str, custom_prompt: str = None) -> str:
    """Generate a complete summary for a single topic using prompts_config.json."""
    init_gemini()
    
    # Load prompt from config file if no custom prompt provided
    if not custom_prompt:
        try:
            with open("prompts_config.json", "r", encoding="utf-8") as f:
                prompts_config = json.load(f)
            custom_prompt = prompts_config.get(topic, {}).get("prompt")
        except FileNotFoundError:
            print(f"prompts_config.json not found, using default for {topic}")
    
    print(f"Generating summary for {topic}...") 
    summary = summarize_from_file(topic, custom_prompt)
    
    return summary

def generate_separate_summaries(articles_by_topic: dict, today_date: str):
    """Generate separate summaries for each topic from saved article files."""
    prompts = json.load(open("prompts_config.json"))
    summaries = {}
    
    for topic in ["ai", "cybersecurity", "web3"]:
        if topic not in articles_by_topic or not articles_by_topic[topic]:
            print(f"⚠️ No {topic} articles")
            continue

        articles = articles_by_topic[topic][:5]  # Top 5
        sources = "\n".join([f"SOURCE {i+1}: {art['title']} - {art['published']}" 
                           for i, art in enumerate(articles)])
        
        prompt = prompts[topic]["prompt"].format(today_date=today_date)
        full_prompt = prompt + f"\n\nSources:\n{sources}"
        
        # Use your existing summarize_from_file logic but with articles
        summary = call_gemini_directly(full_prompt)  # See below
        
        summaries[topic] = summary
        with open(f"{topic}_summary.txt", "w") as f:
            f.write(summary)
        print(f"✅ {topic} summary saved")
    
    return summaries

def call_gemini_directly(prompt: str) -> str:
    init_gemini()
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text
