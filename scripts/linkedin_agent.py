"""
LinkedIn Content Creator using LangChain 1.0

This script implements an AI-powered content creator that:
1. Searches for trending AI/Automation/Low-Code content
2. Retrieves previously used themes from Google Sheets
3. Generates engaging LinkedIn posts with title and content
4. Creates image prompts for visual content
"""

import os
import json
import requests
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from sheets_manager import get_recent_themes


def brave_search(query: str) -> str:
    """
    Search the web using Brave Search API.
    
    Args:
        query: Search query string
        
    Returns:
        JSON string with search results
    """
    api_key = os.environ.get("BRAVE_SEARCH_API_KEY")
    if not api_key:
        return json.dumps({"error": "BRAVE_SEARCH_API_KEY not found in environment"})
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    params = {"q": query, "count": 10}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract web results
        results = []
        for item in data.get("web", {}).get("results", [])[:5]:
            results.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "url": item.get("url", "")
            })
        
        return json.dumps({"results": results})
    except Exception as e:
        return json.dumps({"error": str(e), "results": []})


def generate_linkedin_content(model_name: str = "gemini-1.5-flash") -> Dict[str, Any]:
    """
    Generate LinkedIn post content using AI.
    
    Args:
        model_name: Google Gemini model to use
        
    Returns:
        Dictionary with title, content, and image_prompt
    """
    # Initialize model
    api_key = os.environ.get("GOOGLE_API_KEY")
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.7
    )
    
    # Get used themes from Google Sheets
    print("📊 Fetching used themes from Google Sheets...")
    try:
        used_themes = get_recent_themes(limit=20)
        print(f"Found {len(used_themes)} used themes")
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch used themes: {e}")
        used_themes = []
    
    # Search for trending content
    print("🔍 Searching for trending AI/Automation content...")
    search_query = "latest AI automation low-code no-code news 2026"
    search_results = brave_search(search_query)
    
    # Content generation prompt
    system_prompt = """You are an AI Content Strategist for Guilherme's LinkedIn profile.

Guilherme is an n8n developer, specialist in Low-Code, No-Code, and Artificial Intelligence. He works with automations, AI agent creation, chatbots, and process optimization. Tools: n8n, Make, Zapier, Bubble.io, Framer, ManyChat, Typebot, Supabase, Flowise, and various AI APIs.

Contact: WhatsApp 21977709013 | Email: guifaceads@gmail.com

YOUR TASK:
1. Analyze the search results for AI/Automation/Low-Code topics
2. Choose ONE compelling and recent topic that is NOT in the used themes list
3. Create an engaging LinkedIn post following these guidelines:

CONTENT GUIDELINES:
- Create a strong hook at the beginning (evoke pain, curiosity, or personal dilemma)
- Use engaging narrative that leads to reflection
- Include a call to action at the end
- Avoid corporate language; use human, informal, direct tone
- 250-300 words max
- Mention tools like n8n, Make, or AI agents if relevant
- Write in English
- NO ** formatting
- NO emojis

OUTPUT FORMAT (JSON):
{
  "title": "Hook-based title without **",
  "content": "Full post (250-300 words, English, no emojis, no **)"
}"""
    
    user_prompt = f"""Used Themes (AVOID THESE):
{json.dumps(used_themes, indent=2)}

Search Results:
{search_results}

Based on these results, create a compelling LinkedIn post for Guilherme. Choose a recent topic NOT in the used themes list. Return ONLY valid JSON with 'title' and 'content' keys."""
    
    print("📝 Generating LinkedIn post content...")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = model.invoke(messages)
    content_text = response.content
    
    # Parse JSON from response
    try:
        import re
        json_match = re.search(r'\{[\s\S]*"title"[\s\S]*"content"[\s\S]*\}', content_text)
        if json_match:
            post_data = json.loads(json_match.group(0))
        else:
            post_data = json.loads(content_text)
    except json.JSONDecodeError as e:
        print(f"⚠️ Warning: Could not parse JSON: {e}")
        print(f"Response: {content_text[:200]}...")
        post_data = {
            "title": "AI & Automation Insights",
            "content": content_text[:300] if len(content_text) > 300 else content_text
        }
    
    print(f"✅ Post generated: {post_data.get('title', 'N/A')}")
    
    # Generate image prompt
    print("🎨 Generating image prompt...")
    image_system_prompt = """You are an AI Visual Prompt Generator.

Create a descriptive prompt for generating an AI image that complements LinkedIn post content.

RULES:
- Analyze the post theme and translate emotions into a striking visual scene
- Create flat design, bold colors, or minimalist digital mockup style
- Avoid generic office images; use visual metaphors
- Output a single descriptive prompt in English (NOT JSON)
- Style: modern, professional, eye-catching"""
    
    image_user_prompt = f"""Generate an image prompt for this post:

{post_data.get('content', '')}

Return ONLY the image prompt description, no JSON."""
    
    image_messages = [
        SystemMessage(content=image_system_prompt),
        HumanMessage(content=image_user_prompt)
    ]
    
    image_response = model.invoke(image_messages)
    image_prompt = image_response.content.strip()
    
    print(f"✅ Image prompt generated: {image_prompt[:80]}...")
    
    return {
        "title": post_data.get("title", ""),
        "content": post_data.get("content", ""),
        "image_prompt": image_prompt
    }


def main():
    """
    Main execution function for LinkedIn content generation.
    """
    print("=" * 50)
    print("LINKEDIN CONTENT GENERATOR")
    print("=" * 50)
    
    # Generate content
    output = generate_linkedin_content()
    
    # Save to JSON file
    output_file = "linkedin_post.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Output saved to {output_file}")
    print("\n" + "=" * 50)
    print("FINAL OUTPUT:")
    print("=" * 50)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    return output


if __name__ == "__main__":
    main()
