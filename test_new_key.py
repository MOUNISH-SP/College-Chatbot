import os
import requests
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test the new API key
api_key = os.getenv("GROK_API_KEY", "")

print("🔑 Testing New Grok API Key...")
print(f"API Key: {api_key[:20]}...{api_key[-10:]}")

# Test models endpoint first
models_url = "https://api.x.ai/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    print("\n📋 Checking available models...")
    response = requests.get(models_url, headers=headers, timeout=30, verify=False)
    print(f"Models API Status: {response.status_code}")
    
    if response.status_code == 200:
        models = response.json().get("data", [])
        print("✅ Available models:")
        for model in models:
            print(f"  - {model.get('id')}")
        
        # Test chat completion with first available model
        if models:
            model_name = models[0].get('id')
            print(f"\n🤖 Testing chat with model: {model_name}")
            
            chat_url = "https://api.x.ai/v1/chat/completions"
            data = {
                "model": model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful college assistant."
                    },
                    {
                        "role": "user",
                        "content": "Hello! Can you help me with information about Kongu Engineering College?"
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.3
            }
            
            chat_response = requests.post(chat_url, headers=headers, json=data, timeout=30, verify=False)
            print(f"Chat API Status: {chat_response.status_code}")
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                answer = result["choices"][0]["message"]["content"]
                print(f"✅ Chat Success: {answer.strip()}")
                print("\n🎉 GROK API IS WORKING!")
            else:
                print(f"❌ Chat Error: {chat_response.status_code} - {chat_response.text}")
    else:
        print(f"❌ Models Error: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print(f"\n🌐 Chatbot is running at: http://127.0.0.1:5000")
print("🎯 Test questions to ask:")
print("  - What engineering programs are offered?")
print("  - How are placement opportunities?")
