"""
Gemini Image Generator using official Google GenAI SDK

Generates images from text prompts using Google's Gemini 2.5 Flash Image model.
"""

import os
import json
import sys
from typing import Optional
from google import genai
from google.genai import types


def generate_image(prompt: str) -> Optional[str]:
    """
    Generate an image using Gemini 2.5 Flash Image.
    
    Args:
        prompt: Text description of the image to generate
        
    Returns:
        Path to saved image file or None if generation failed
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        return None
    
    try:
        print(f"🎨 Generating image with Gemini 2.5 Flash Image...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Initialize client
        client = genai.Client(api_key=api_key)
        
        # Generate image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt],
        )
        
        # Save generated image
        image_saved = False
        output_path = "linkedin_image.png"
        
        for part in response.parts:
            if part.text is not None:
                print(f"📄 Model response: {part.text}")
            elif part.inline_data is not None:
                # Convert to PIL Image and save
                image = part.as_image()
                image.save(output_path)
                print(f"✅ Image generated successfully!")
                print(f"💾 Image saved to {output_path}")
                image_saved = True
                break
        
        if not image_saved:
            print("⚠️ Warning: No image data found in response")
            return None
            
        return output_path
            
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
