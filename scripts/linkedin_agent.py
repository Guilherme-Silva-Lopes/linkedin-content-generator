"""
LinkedIn Content Creator Agent using LangChain 1.0

This script implements an AI agent that:
1. Searches for trending AI/Automation/Low-Code content
2. Retrieves previously used themes from Google Sheets
3. Generates engaging LinkedIn posts with title and content
4. Creates image prompts for visual content
"""

import os
import json
from typing import List, Dict, Any
from langchain.agents import create_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import requests


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
    params = {"q": query}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return json.dumps(response.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_used_themes() -> str:
    """
    Retrieves recently used themes from Google Sheets to avoid repetition.
    
    Returns:
        JSON string with list of theme titles
    """
    # This will be imported from sheets_manager
    from sheets_manager import get_recent_themes
    
    try:
        themes = get_recent_themes(limit=20)
        return json.dumps({"themes": themes})
    except Exception as e:
        return json.dumps({"error": str(e), "themes": []})


def create_content_agent(model_name: str = "gemini-2.0-flash-exp"):
    """
    Creates the main content generation agent with search capabilities.
    
    Args:
        model_name: Google Gemini model to use
        
    Returns:
        LangChain agent configured for content creation
    """
    # Initialize the model
    api_key = os.environ.get("GOOGLE_API_KEY")
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.4
    )
    
    # Define tools
    tools = [
        Tool(
            name="brave_search_tool",
            func=brave_search,
            description="Always use this to search for current content on the internet about AI, Automation, Low-Code, and No-Code topics. Returns JSON with search results."
        ),
        Tool(
            name="get_used_themes_tool",
            func=get_used_themes,
            description="Retrieves a list of recently used post themes/titles from Google Sheets to avoid repetition. Returns JSON with themes array."
        )
    ]
    
    # System prompt for content creator
    system_prompt = """
{
  "role": "AI & Automation Content Strategist for Guilherme's LinkedIn Profile",
  "goal": "To proactively find, research, and create a compelling LinkedIn post based on current news and trends in AI, Automation, and Technology, tailored to Guilherme's professional profile.",
  "context": {
    "profile_owner": {
      "name": "Guilherme",
      "bio": "n8n developer, specialist in Low-Code, No-Code, and Artificial Intelligence. Works with automations, AI agent creation, chatbots, and solutions for process optimization. Uses platforms like n8n, Make, Zapier, Bubble.io, Framer, ManyChat, Typebot, Supabase, Flowise, and various AI APIs. Creates everything from CRMs to intelligent assistants for sales and customer service. Is constantly learning new no-code and low-code tools.",
      "tools": [
        "n8n", "Make", "Zapier", "Activepieces", "Supabase", "WordPress", "Redis",
        "ManyChat", "Typebot", "Flowise", "ChatGPT", "Gemini", "Claude",
        "Baserow", "Airtable", "Notion", "Google Workspace"
      ],
      "contact": {
        "whatsapp": "21977709013",
        "email": "guifaceads@gmail.com"
      }
    },
    "audience_persona": "Developers, tech entrepreneurs, and business managers interested in process optimization, low-code solutions, and implementing AI."
  },
  "workflow": [
    {
      "step": 1,
      "action": "Get Used Themes",
      "instruction": "Use the get_used_themes_tool to retrieve recently used post themes and avoid repetition."
    },
    {
      "step": 2,
      "action": "Broad Scan",
      "instruction": "Use the brave_search_tool to find the latest news, trending articles, and insightful discussions about Artificial Intelligence, Automations, Low-Code, and No-Code. Focus on recent breakthroughs, new tool releases, or surprising case studies from the last week or two."
    },
    {
      "step": 3,
      "action": "Topic Selection",
      "instruction": "From the search results, analyze and select a single, compelling topic that is highly relevant to Guilherme's expertise and would likely spark a conversation. The topic MUST NOT be in the list of used themes."
    },
    {
      "step": 4,
      "action": "Deep Dive Research",
      "instruction": "Perform a new, focused search on the selected topic using brave_search_tool. Gather specific details, key data points, expert opinions, or underlying implications."
    },
    {
      "step": 5,
      "action": "Create Post",
      "instruction": "Generate an engaging LinkedIn post following the content guidelines below."
    }
  ],
  "content_guidelines": [
    "Create a strong hook right at the beginning. It should evoke pain, curiosity, or a personal dilemma related to the no-code, automation, or AI universe. Avoid generic titles.",
    "Incorporate real or inspired experiences from Guilherme's journey, especially situations of failure, frustrated experiments, or discoveries in projects with automations, agents, or AI.",
    "Use an engaging narrative structure that leads to reflection and encourages comments.",
    "Include a call to action at the end (e.g., ask to comment, send a DM, or share).",
    "Avoid corporate language; use a human, informal, direct, and approachable tone.",
    "Limit the post to 250–300 words to maintain engagement.",
    "Mention, if relevant, tools like n8n, Make, or the AI agents that Guilherme uses.",
    "Generate the post in English.",
    "Do not use ** in the text.",
    "Do not use emojis in the text.",
    "The title should be compelling and hook-based, avoiding generic headlines."
  ],
  "output_format": {
    "title": "An engaging hook-based title without ** (e.g., 'My Low-Code Automations Hit a Wall. Then AI Became the Ultimate Co-Pilot.')",
    "content": "The full LinkedIn post text (250-300 words, English, no emojis, no **)"
  },
  "rules": [
    "You MUST use both tools (brave_search_tool and get_used_themes_tool).",
    "The output must be a valid JSON object with 'title' and 'content' keys.",
    "The chosen topic must be recent and NOT in the used themes list.",
    "Focus on storytelling and vulnerability rather than just teaching."
  ]
}
"""
    
    # Create agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agent


def create_image_prompt_agent(model_name: str = "gemini-2.0-flash-exp"):
    """
    Creates an agent specifically for generating image prompts.
    
    Args:
        model_name: Google Gemini model to use
        
    Returns:
        LangChain agent configured for image prompt generation
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.6
    )
    
    system_prompt = """
{
  "role": "AI agent that generates visual prompts for LinkedIn post images",
  "goal": "Generate a clear and effective prompt to create an image that visually complements the post content",
  "instructions": [
    "Analyze the central theme of the post and translate the emotion (curiosity, frustration, overcoming, etc.) into a striking visual scene.",
    "Create a prompt that describes an illustration-style image or minimalist digital mockup that will grab attention in the LinkedIn feed.",
    "Avoid generic office images. Prefer visual metaphors (e.g., a broken staircase to represent failure).",
    "Describe the image in English for use with image generation models.",
    "Include the desired visual style (e.g., flat design, bold colors, isometric, 3D, etc.)",
    "The output should be a single descriptive prompt string, not JSON."
  ],
  "output_format": "Descriptive prompt in English to generate AI image"
}
"""
    
    agent = create_agent(
        model=model,
        tools=[],  # No tools needed for image prompt
        system_prompt=system_prompt
    )
    
    return agent


def main():
    """
    Main execution function for LinkedIn content generation.
    """
    # Step 1: Create content with research
    print("🔍 Creating content agent...")
    content_agent = create_content_agent()
    
    print("📝 Generating LinkedIn post...")
    content_result = content_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": "Find current content to create a post for Guilherme's LinkedIn. Make sure to avoid topics that have already been used."
            }
        ]
    })
    
    # Extract the content from agent response
    # The agent should return JSON in the final message
    final_message = content_result["messages"][-1]["content"]
    
    # Try to parse JSON from the response
    try:
        # Sometimes the response might have markdown code blocks
        import re
        json_match = re.search(r'\{[\s\S]*"title"[\s\S]*"content"[\s\S]*\}', final_message)
        if json_match:
            post_data = json.loads(json_match.group(0))
        else:
            # Fallback: assume entire message is JSON
            post_data = json.loads(final_message)
    except json.JSONDecodeError:
        print("⚠️ Warning: Could not parse JSON from agent response. Using fallback structure.")
        post_data = {
            "title": "Generated content - check logs",
            "content": final_message
        }
    
    print(f"✅ Post generated!")
    print(f"📌 Title: {post_data.get('title', 'N/A')}")
    print(f"📄 Content length: {len(post_data.get('content', ''))} chars")
    
    # Step 2: Generate image prompt
    print("\n🎨 Creating image prompt agent...")
    image_agent = create_image_prompt_agent()
    
    print("🖼️ Generating image prompt...")
    image_result = image_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"Generate an image prompt for this LinkedIn post:\n\n{post_data.get('content', '')}"
            }
        ]
    })
    
    image_prompt = image_result["messages"][-1]["content"]
    print(f"✅ Image prompt generated!")
    print(f"🎨 Prompt: {image_prompt[:100]}...")
    
    # Step 3: Save outputs to JSON file
    output = {
        "title": post_data.get("title", ""),
        "content": post_data.get("content", ""),
        "image_prompt": image_prompt
    }
    
    output_file = "linkedin_post.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Output saved to {output_file}")
    print("\n" + "="*50)
    print("FINAL OUTPUT:")
    print("="*50)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    return output


if __name__ == "__main__":
    main()
