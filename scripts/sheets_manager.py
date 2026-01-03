"""
Google Sheets Manager for LinkedIn Content Tracker

Handles reading and writing themes to/from Google Sheets to track published content.
"""

import os
import json
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Google Sheets API configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1g7ZLdPYc8-XyKIexgHhpot8HTtcAv5uQmMXjBK4QUEo'
SHEET_NAME = 'Sheet1'


def get_credentials() -> Credentials:
    """
    Authenticate with Google Sheets API using service account or OAuth.
    
    Returns:
        Google API credentials
    """
    creds = None
    
    # Check for service account credentials in environment
    service_account_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
    
    if service_account_json:
        # Use service account
        from google.oauth2 import service_account
        creds_dict = json.loads(service_account_json)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES
        )
    else:
        # Fallback to OAuth flow (for local development)
        token_file = 'token.json'
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise ValueError(
                    "No valid credentials found. Please set GOOGLE_SHEETS_CREDENTIALS "
                    "environment variable with service account JSON."
                )
    
    return creds


def get_recent_themes(limit: int = 20) -> List[str]:
    """
    Retrieve the most recent themes from Google Sheets.
    
    Args:
        limit: Maximum number of themes to retrieve
        
    Returns:
        List of theme strings (post titles)
    """
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        # Read values from TEMA column (assuming column A)
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A:A'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            print("ℹ️ No themes found in sheet")
            return []
        
        # Skip header row and get last N themes
        themes = [row[0] for row in values[1:] if row]  # Skip empty rows
        recent_themes = themes[-limit:] if len(themes) > limit else themes
        
        print(f"📊 Retrieved {len(recent_themes)} recent themes from Google Sheets")
        return recent_themes
        
    except HttpError as error:
        print(f"❌ Google Sheets API error: {error}")
        return []
    except Exception as e:
        print(f"❌ Error retrieving themes: {e}")
        return []


def add_theme(theme: str) -> bool:
    """
    Add a new theme to Google Sheets.
    
    Args:
        theme: The post title/theme to add
        
    Returns:
        True if successful, False otherwise
    """
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        # Append new row with theme
        values = [[theme]]
        body = {'values': values}
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f'{SHEET_NAME}!A:A',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        print(f"✅ Added theme to Google Sheets: {theme}")
        print(f"📝 Updated cells: {result.get('updates').get('updatedCells')}")
        return True
        
    except HttpError as error:
        print(f"❌ Google Sheets API error: {error}")
        return False
    except Exception as e:
        print(f"❌ Error adding theme: {e}")
        return False


def main():
    """
    Test function for sheets manager.
    """
    print("Testing Google Sheets Manager...")
    print("="*50)
    
    # Test 1: Get recent themes
    print("\n📖 Test 1: Get recent themes")
    themes = get_recent_themes(limit=5)
    for i, theme in enumerate(themes, 1):
        print(f"{i}. {theme}")
    
    # Test 2: Add a theme (commented out to avoid accidental writes)
    # print("\n✍️ Test 2: Add a theme")
    # success = add_theme("Test Theme - " + str(int(time.time())))
    # print(f"Success: {success}")


if __name__ == "__main__":
    main()
