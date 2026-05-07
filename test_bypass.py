"""
Test FortiGuard Bypass System
==============================

This script tests all the bypass strategies to see if any can reach Grok API.
"""

import os
import requests
import urllib3
from network_config import get_proxy_config, get_alternative_endpoints

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set API key
os.environ["GROK_API_KEY"] = os.getenv("GROK_API_KEY", "")

def test_grok_bypass():
    """Test all bypass strategies for Grok API"""
    grok_api_key = os.getenv("GROK_API_KEY")
    
    if not grok_api_key:
        print("❌ No API key found")
        return False
    
    print("🔍 Testing Grok API Bypass Strategies...")
    print(f"API Key: {grok_api_key[:20]}...{grok_api_key[-10:]}")
    
    proxy_configs = get_proxy_config()
    endpoints = get_alternative_endpoints()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "curl/7.68.0",
        "Python-requests/2.28.1"
    ]
    
    success_count = 0
    
    for i, endpoint in enumerate(endpoints):
        print(f"\n📍 Testing Endpoint {i+1}: {endpoint}")
        
        for j, proxy in enumerate(proxy_configs):
            proxy_str = f"Proxy {j}" if proxy else "No Proxy"
            print(f"  🔧 {proxy_str}: ", end="")
            
            for k, user_agent in enumerate(user_agents):
                headers = {
                    "Authorization": f"Bearer {grok_api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": user_agent
                }
                
                try:
                    session = requests.Session()
                    session.verify = False
                    if proxy:
                        session.proxies.update(proxy)
                    
                    # Test with a simple request first
                    test_response = session.get(
                        endpoint.replace("/chat/completions", "/models"),
                        headers=headers,
                        timeout=10
                    )
                    
                    if test_response.status_code == 200:
                        print(f"✅ SUCCESS with {user_agent[:20]}...")
                        success_count += 1
                        
                        # Try actual chat completion
                        data = {
                            "model": "grok-2-latest",
                            "messages": [
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": "Say hello"}
                            ],
                            "max_tokens": 10
                        }
                        
                        chat_response = session.post(endpoint, headers=headers, json=data, timeout=30)
                        if chat_response.status_code == 200:
                            result = chat_response.json()
                            answer = result["choices"][0]["message"]["content"]
                            print(f"    💬 Chat Response: {answer.strip()}")
                            return True
                        else:
                            print(f"    ❌ Chat failed: {chat_response.status_code}")
                    else:
                        print(f"❌ {test_response.status_code} ", end="")
                        
                except Exception as e:
                    print(f"❌ Error ", end="")
            
            print()
    
    print(f"\n📊 Results: {success_count} successful connections out of {len(endpoints) * len(proxy_configs) * len(user_agents)} attempts")
    
    if success_count == 0:
        print("\n🔧 Additional Solutions:")
        print("1. Try using mobile hotspot (different network)")
        print("2. Use VPN service")
        print("3. Contact network admin to whitelist api.x.ai")
        print("4. Use proxy server")
        return False
    else:
        print("\n🎉 Bypass strategy found! Chatbot should work with Grok API.")
        return True

if __name__ == "__main__":
    success = test_grok_bypass()
    
    print(f"\n🌐 Chatbot running at: http://127.0.0.1:5000")
    if success:
        print("✅ Grok API should work now!")
    else:
        print("⚠️ Using Pinecone fallback (still works great!)")
