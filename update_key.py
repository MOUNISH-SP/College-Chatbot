"""
Update Grok API Key for Kongu Chatbot
=====================================

INSTRUCTIONS:
1. Run this script
2. Enter your new API key when prompted
3. The script will test and update the system

"""

import os
import requests

def test_and_update_key():
    print("=== KONGU CHATBOT - GROK API KEY UPDATER ===")
    print("\nPlease enter your new API key (named 'Kongu Chatbot'):")
    
    # Get the new API key
    new_key = input("New API Key: ").strip()
    
    if len(new_key) < 20:
        print("❌ API key seems too short. Please check and try again.")
        return False
    
    print(f"\n🔑 Testing new API key...")
    
    # Test the API key
    url = "https://api.x.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {new_key}",
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
            
            print(f"\n🚀 TO START CHATBOT WITH NEW KEY:")
            print(f"set GROK_API_KEY={new_key}")
            print(f"\n🌐 OR RUN FLASK DIRECTLY:")
            print(f'$env:GROK_API_KEY="{new_key}"; python app.py')
            
            # Save to a temporary file for easy copy-paste
            with open('current_api_key.txt', 'w') as f:
                f.write(new_key)
            print(f"\n💾 API key saved to 'current_api_key.txt' for reference")
            
            return True
        else:
            print(f"❌ API Key INVALID: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_and_update_key()
    if success:
        print("\n✅ Ready to start chatbot with new API key!")
    else:
        print("\n❌ Please check your API key and try again.")
