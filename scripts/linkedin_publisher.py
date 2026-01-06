"""
LinkedIn Publisher

Publishes posts to LinkedIn using the LinkedIn API and updates Google Sheets.
"""

import os
import json
import sys
import base64
from typing import Optional, Dict, Any
import requests
from sheets_manager import add_theme


# LinkedIn API Configuration
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

# ⚠️ IMPORTANT: Replace with your LinkedIn Person URN
# Get your Person URN by following the instructions in CREDENTIALS_SETUP.md
PERSON_URN = "urn:li:person:YOUR_PERSON_URN_HERE"


def get_linkedin_access_token() -> str:
    """
    Get LinkedIn access token from environment variables.
    
    Returns:
        LinkedIn OAuth2 access token
    """
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if not token:
        raise ValueError("LINKEDIN_ACCESS_TOKEN not found in environment variables")
    return token


def upload_image_to_linkedin(image_base64: str, access_token: str) -> Optional[str]:
    """
    Upload an image to LinkedIn and get the asset URN.
    
    Args:
        image_base64: Base64-encoded image data
        access_token: LinkedIn OAuth2 access token
        
    Returns:
        Asset URN string or None if upload failed
    """
    try:
        # Step 1: Register upload
        register_url = f"{LINKEDIN_API_BASE}/assets?action=registerUpload"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": PERSON_URN,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        
        print("📤 Registering image upload with LinkedIn...")
        register_response = requests.post(
            register_url,
            headers=headers,
            json=register_payload,
            timeout=30
        )
        register_response.raise_for_status()
        register_data = register_response.json()
        
        # Extract upload URL and asset URN
        upload_url = register_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        asset_urn = register_data["value"]["asset"]
        
        print(f"✅ Upload registered. Asset URN: {asset_urn}")
        
        # Step 2: Upload the image binary
        image_bytes = base64.b64decode(image_base64)
        
        upload_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/png"
        }
        
        print("📤 Uploading image binary...")
        upload_response = requests.put(
            upload_url,
            headers=upload_headers,
            data=image_bytes,
            timeout=60
        )
        upload_response.raise_for_status()
        
        print("✅ Image uploaded successfully!")
        return asset_urn
        
    except Exception as e:
        print(f"❌ Error uploading image to LinkedIn: {e}")
        return None


def create_linkedin_post(
    text: str,
    image_asset_urn: Optional[str] = None,
    access_token: Optional[str] = None
) -> bool:
    """
    Create a post on LinkedIn.
    
    Args:
        text: The post content text
        image_asset_urn: Optional asset URN for image attachment
        access_token: LinkedIn OAuth2 access token
        
    Returns:
        True if successful, False otherwise
    """
    if access_token is None:
        access_token = get_linkedin_access_token()
    
    url = f"{LINKEDIN_API_BASE}/ugcPosts"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    # Build the post payload
    payload: Dict[str, Any] = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # Add image if provided
    if image_asset_urn:
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {
                "status": "READY",
                "media": image_asset_urn
            }
        ]
        print("🖼️ Post will include image")
    else:
        print("📝 Post will be text-only")
    
    try:
        print("📤 Publishing post to LinkedIn...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        post_id = response.headers.get("x-restli-id", "unknown")
        print(f"✅ Post published successfully! ID: {post_id}")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error publishing post: {e}")
        print(f"📄 Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error publishing post: {e}")
        return False


def main():
    """
    Main execution function for LinkedIn publishing.
    Reads post data from linkedin_post.json and publishes to LinkedIn.
    """
    # Load post data
    input_file = "linkedin_post.json"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found. Run linkedin_agent.py first.")
        sys.exit(1)
    
    with open(input_file, "r", encoding="utf-8") as f:
        post_data = json.load(f)
    
    title = post_data.get("title", "")
    content = post_data.get("content", "")
    
    if not content:
        print("❌ Error: No content found in linkedin_post.json")
        sys.exit(1)
    
    # Check for image file
    image_file = "linkedin_image.png"
    image_base64 = None
    
    if os.path.exists(image_file):
        # Check if file has content (not a placeholder)
        file_size = os.path.getsize(image_file)
        if file_size > 0:
            print(f"\n🖼️ Image file detected: {image_file} ({file_size} bytes)")
            try:
                with open(image_file, "rb") as img_f:
                    image_base64 = base64.b64encode(img_f.read()).decode('utf-8')
                print(f"✅ Image loaded and encoded ({len(image_base64)} chars)")
            except Exception as e:
                print(f"⚠️ Warning: Failed to load image file: {e}")
                image_base64 = None
        else:
            print(f"\n📝 Image file is empty (placeholder), will post text only")
    else:
        print("\n📝 No image file found, will post text only")
    
    # Get LinkedIn access token
    try:
        access_token = get_linkedin_access_token()
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Upload image if present
    image_asset_urn = None
    if image_base64:
        print("\n🖼️ Image detected, uploading to LinkedIn...")
        image_asset_urn = upload_image_to_linkedin(image_base64, access_token)
        if not image_asset_urn:
            print("⚠️ Image upload failed, will post without image")
    
    # Publish post
    print("\n📝 Publishing post...")
    print(f"Title: {title}")
    print(f"Content length: {len(content)} chars")
    
    success = create_linkedin_post(
        text=content,
        image_asset_urn=image_asset_urn,
        access_token=access_token
    )
    
    if success:
        # Update Google Sheets with the new theme
        print("\n📊 Updating Google Sheets...")
        sheets_success = add_theme(title)
        
        if sheets_success:
            print("✅ Google Sheets updated successfully")
        else:
            print("⚠️ Warning: Failed to update Google Sheets, but post was published")
        
        # Save result
        result = {
            "success": True,
            "published": True,
            "has_image": image_asset_urn is not None,
            "sheets_updated": sheets_success
        }
        
        print("\n" + "="*50)
        print("✅ POST PUBLISHED SUCCESSFULLY!")
        print("="*50)
    else:
        result = {
            "success": False,
            "published": False,
            "error": "Failed to publish post to LinkedIn"
        }
        
        print("\n" + "="*50)
        print("❌ POST PUBLICATION FAILED")
        print("="*50)
        sys.exit(1)
    
    # Save result
    with open("publish_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
