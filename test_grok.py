import os
import requests

# Set the API key directly for testing
os.environ["GROK_API_KEY"] = "6ruv782h9cSepTusILB1lZLwhGQ0znfR7fVZ4ygaDC7bOm31TiF7jixjXouu7yqV8mxIvQ8Pot3dTDKx"

def test_grok_api():
    """Test Grok API integration"""
    grok_api_key = os.getenv("GROK_API_KEY")
    print(f"GROK_API_KEY found: {bool(grok_api_key)}")
    print(f"API Key length: {len(grok_api_key) if grok_api_key else 0}")
    
    if not grok_api_key:
        return "Grok API key not found"
    
    # First try to get available models
    models_url = "https://api.x.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {grok_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("Getting available models...")
        response = requests.get(models_url, headers=headers, timeout=30)
        print(f"Models response status: {response.status_code}")
        
        if response.status_code == 200:
            models_data = response.json()
            print("Available models:")
            for model in models_data.get("data", []):
                print(f"  - {model.get('id')}")
        else:
            print(f"Models API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Models API Error: {str(e)}")
    
    # Try with a common model name
    url = "https://api.x.ai/v1/chat/completions"
    
    data = {
        "model": "grok-2-latest",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful college assistant. Answer only using the provided context. If information is not in context, say you don't know."
            },
            {
                "role": "user",
                "content": """Context:
Kongu Engineering College offers B.E. Computer Science and Engineering, B.E. Civil Engineering, B.E. Mechanical Engineering programs. The college has a placement rate of 95% with top recruiters like TCS, Infosys, and Wipro.

Question:
What engineering programs are available at Kongu Engineering College?"""
            }
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    try:
        print("\nMaking API call to Grok...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return f"✅ Grok API Success: {answer.strip()}"
        else:
            return f"❌ API Error: {response.status_code} - {response.text}"
        
    except requests.exceptions.RequestException as e:
        return f"❌ Request failed: {str(e)}"
    except KeyError as e:
        return f"❌ Response format error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    result = test_grok_api()
    print(result)
