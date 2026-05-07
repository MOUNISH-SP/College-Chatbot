"""
Grok API Setup Guide for Kongu Chatbot
=====================================

STEPS TO GET GROK API KEY:
1. Go to https://console.x.ai
2. Sign up/login to your X/Twitter account
3. Navigate to API section
4. Create new API key
5. Copy the API key

CURRENT INTEGRATION STATUS:
- ✅ Pinecone RAG working perfectly
- ✅ Retrieval system working
- ✅ Fallback system working
- ⚠️ Grok API key needs valid key

TEST YOUR CURRENT SETUP:
Run this to test if your key works:
"""

import os
import requests

def test_grok_key(api_key):
    """Test if Grok API key is valid"""
    url = "https://api.x.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print("✅ API Key is VALID!")
            print("Available models:")
            for model in models:
                print(f"  - {model.get('id')}")
            return True
        else:
            print(f"❌ API Key INVALID: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== GROK API KEY TESTER ===")
    api_key = input("Enter your Grok API key: ").strip()
    
    if len(api_key) < 20:
        print("❌ API key seems too short")
    else:
        is_valid = test_grok_key(api_key)
        
        if is_valid:
            print(f"\n✅ SET THIS ENVIRONMENT VARIABLE:")
            print(f"set GROK_API_KEY={api_key}")
            print(f"\n✅ OR RUN FLASK LIKE THIS:")
            print(f'$env:GROK_API_KEY="{api_key}"; python app.py')
