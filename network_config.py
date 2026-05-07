"""
Network Configuration for FortiGuard Bypass
===========================================

This file contains network configurations to bypass FortiGuard firewall
and enable Grok API access.
"""

import os
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_proxy_config():
    """Get proxy configuration for network bypass"""
    # Common proxy ports that might work
    proxy_configs = [
        None,  # No proxy
        {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080'
        },
        {
            'http': 'http://127.0.0.1:3128',
            'https': 'http://127.0.0.1:3128'
        },
        {
            'http': 'socks5://127.0.0.1:1080',
            'https': 'socks5://127.0.0.1:1080'
        }
    ]
    return proxy_configs

def get_alternative_endpoints():
    """Get alternative endpoints that might bypass firewall"""
    return [
        "https://api.x.ai/v1/chat/completions",
        "https://api.x.ai:443/v1/chat/completions",
        "https://api.x.ai:8443/v1/chat/completions"
    ]

def test_network_connectivity():
    """Test if we can reach external APIs"""
    test_urls = [
        "https://httpbin.org/get",
        "https://api.openai.com/v1/models",
        "https://api.x.ai/v1/models"
    ]
    
    results = {}
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10, verify=False)
            results[url] = {
                "status": response.status_code,
                "accessible": response.status_code < 400
            }
        except Exception as e:
            results[url] = {
                "status": "Error",
                "accessible": False,
                "error": str(e)
            }
    
    return results

if __name__ == "__main__":
    print("🔍 Testing Network Connectivity...")
    results = test_network_connectivity()
    
    for url, result in results.items():
        status = "✅" if result["accessible"] else "❌"
        print(f"{status} {url}: {result['status']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    print("\n🌐 Alternative Endpoints:")
    for endpoint in get_alternative_endpoints():
        print(f"  - {endpoint}")
    
    print("\n🔧 Proxy Configurations:")
    for i, proxy in enumerate(get_proxy_config()):
        if proxy:
            print(f"  - Config {i}: {proxy}")
        else:
            print(f"  - Config {i}: No proxy")
