"""
Gemini Image Generator using Gemini 2.5 Flash Image API

Generates images from text prompts using Google's Gemini image generation model.
"""

import os
import json
import base64
import sys
from typing import Optional


def generate_image(prompt: str, aspect_ratio: str = "1:1") -> Optional[str]:
    """
    Generate an image using Gemini 2.5 Flash Image API.
    
    Args:
        prompt: Text description of the image to generate
        aspect_ratio: Aspect ratio for the image (default: "1:1")
        
    Returns:
        Base64-encoded image data or None if generation failed
    """
    import requests
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        return None
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generation_config": {
            "response_modalities": ["IMAGE"],
            "image_config": {
                "aspect_ratio": aspect_ratio
            }
        }
    }
    
    try:
        print(f"🎨 Generating image with Gemini...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Check finish reason
        finish_reason = result.get("candidates", [{}])[0].get("finishReason", "UNKNOWN")
        
        if finish_reason == "NO_IMAGE":
            print("⚠️ Warning: Image generation returned NO_IMAGE. This may happen due to safety filters.")
            return None
        
        # Extract base64 image data
        try:
            image_data = result["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
            print("✅ Image generated successfully!")
            print(f"📊 Image data length: {len(image_data)} chars")
            return image_data
        except (KeyError, IndexError) as e:
            print(f"❌ Error extracting image from response: {e}")
            print(f"📄 Response structure: {json.dumps(result, indent=2)}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out after 60 seconds")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"📄 Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def save_image(base64_data: str, output_path: str = "generated_image.png") -> bool:
    """
    Save base64-encoded image to file.
    
    Args:
        base64_data: Base64-encoded image data
        output_path: Path to save the image file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        image_bytes = base64.b64decode(base64_data)
        
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        
        print(f"💾 Image saved to {output_path}")
        print(f"📊 File size: {len(image_bytes)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return False


def main():
    """
    Main execution function for image generation.
    Reads prompt from linkedin_post.json and generates image.
    """
    # Load prompt from previous step
    input_file = "linkedin_post.json"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found. Run linkedin_agent.py first.")
        sys.exit(1)
    
    with open(input_file, "r", encoding="utf-8") as f:
        post_data = json.load(f)
    
    image_prompt = post_data.get("image_prompt", "")
    
    if not image_prompt:
        print("❌ Error: No image_prompt found in linkedin_post.json")
        sys.exit(1)
    
    # Generate image
    image_data = generate_image(image_prompt)
    
    if image_data:
        # Save image to file
        save_image(image_data, "linkedin_image.png")
        
        # Update JSON with image data
        post_data["image_base64"] = image_data
        post_data["image_generated"] = True
        
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Updated linkedin_post.json with image data")
        
        # Also save just the base64 for easy consumption
        output = {
            "success": True,
            "image_base64": image_data,
            "finish_reason": "STOP"
        }
    else:
        print("⚠️ Image generation failed, proceeding without image")
        post_data["image_base64"] = None
        post_data["image_generated"] = False
        
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)
        
        output = {
            "success": False,
            "image_base64": None,
            "finish_reason": "NO_IMAGE"
        }
    
    # Save result
    with open("image_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "="*50)
    print("IMAGE GENERATION COMPLETE")
    print("="*50)


if __name__ == "__main__":
    main()
