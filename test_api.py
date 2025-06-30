#!/usr/bin/env python3
"""
Test script for the URL Content Extractor API
"""
import requests
import json
import sys

def test_api(base_url="http://localhost:8000"):
    """Test the API endpoints"""
    
    print("🧪 Testing URL Content Extractor API")
    print(f"📡 API Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Root endpoint
    print("2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    print()
    
    # Test 3: Text-only extraction
    print("3. Testing text-only extraction...")
    test_url = "https://example.com"
    try:
        response = requests.post(
            f"{base_url}/extract/text-only",
            json=test_url,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Text extraction successful")
            print(f"   URL: {data['url']}")
            print(f"   Stats: {data['stats']}")
            print(f"   Text sections: {len(data['content']['text'])}")
        else:
            print(f"❌ Text extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Text extraction error: {e}")
    
    print()
    
    # Test 4: GET method extraction
    print("4. Testing GET method extraction...")
    try:
        response = requests.get(
            f"{base_url}/extract",
            params={
                "url": "https://example.com",
                "include_images": True,
                "include_videos": False
            }
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ GET extraction successful")
            print(f"   URL: {data['url']}")
            print(f"   Stats: {data['stats']}")
        else:
            print(f"❌ GET extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ GET extraction error: {e}")
    
    print()
    
    # Test 5: Full extraction with POST
    print("5. Testing full extraction (POST)...")
    try:
        response = requests.post(
            f"{base_url}/extract",
            json={
                "url": "https://example.com",
                "include_images": True,
                "include_videos": True
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Full extraction successful")
            print(f"   URL: {data['url']}")
            print(f"   Stats: {data['stats']}")
            print(f"   Content types available: {list(data['content'].keys())}")
        else:
            print(f"❌ Full extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Full extraction error: {e}")
    
    print()
    
    # Test 6: Depth extraction
    print("6. Testing depth extraction...")
    try:
        response = requests.post(
            f"{base_url}/extract/depth",
            json={
                "url": "https://example.com",
                "include_images": False,
                "include_videos": False,
                "depth": 1,
                "max_pages": 5,
                "delay": 0.5
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Depth extraction successful")
            print(f"   URL: {data['url']}")
            print(f"   Depth: {data['depth']}")
            print(f"   Stats: {data['stats']}")
        else:
            print(f"❌ Depth extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Depth extraction error: {e}")
    
    print()
    print("🎯 API testing completed!")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_api(base_url)