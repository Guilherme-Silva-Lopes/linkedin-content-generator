"""
OpenAI Image Generator

Generates images from text prompts using OpenAI's gpt-image-1.5 model.
"""

import os
import json
import sys
import requests
from typing import Optional
from openai import OpenAI


def generate_image(prompt: str) -> Optional[str]:
    """
    Generate an image using OpenAI gpt-image-1.5.
    
    Args:
        prompt: Text description of the image to generate
        
    Returns:
        Path to saved image file or None if generation failed
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        return None
    
    try:
        print(f"🎨 Generating image with OpenAI gpt-image-1.5...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Generate image
        response = client.images.generate(
            model="gpt-image-1.5",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        # Extract image URL
        image_url = response.data[0].url
        
        if not image_url:
            print("⚠️ Warning: No image URL found in response")
            return None
            
        # Download and save image
        print(f"⬇️ Downloading image from {image_url[:50]}...")
        img_response = requests.get(image_url)
        
        output_path = "linkedin_image.png"
        
        if img_response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(img_response.content)
            print(f"✅ Image generated and downloaded successfully!")
            print(f"💾 Image saved to {output_path}")
            return output_path
        else:
            print(f"❌ Error downloading image: {img_response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None


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
    image_path = generate_image(image_prompt)
    
    if image_path:
        # Update JSON with image info
        post_data["image_path"] = image_path
        post_data["image_generated"] = True
        
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Updated linkedin_post.json with image data")
        
        # Save result
        output = {
            "success": True,
            "image_path": image_path,
            "finish_reason": "STOP"
        }
    else:
        print("⚠️ Image generation failed, proceeding without image")
        post_data["image_path"] = None
        post_data["image_generated"] = False
        
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=2, ensure_ascii=False)
        
        output = {
            "success": False,
            "image_path": None,
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
