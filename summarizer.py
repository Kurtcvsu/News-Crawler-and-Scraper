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
            import json
            with open("prompts_config.json", "r", encoding="utf-8") as f:
                prompts_config = json.load(f)
            custom_prompt = prompts_config.get(topic, {}).get("prompt")
        except FileNotFoundError:
            print(f"prompts_config.json not found, using default for {topic}")
    
    print(f"Generating summary for {topic}...")
    summary = summarize_from_file(topic, custom_prompt)
    
    return summary

def generate_separate_summaries() -> Dict[str, str]:
    """Generate separate summaries for each topic from saved article files."""
    summaries = {}
    
    for topic in ["ai", "cybersecurity", "web3"]:
        summary = generate_topic_summary(topic)
        if "not found" not in summary.lower():
            summaries[topic] = summary
            
            filename = f"{topic}_summary.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"✅ {topic.upper()} summary saved to {filename}")
        else:
            print(f"⚠️ Skipping {topic}: {summary}")
    
    return summaries


