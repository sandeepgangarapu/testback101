#!/usr/bin/env python3
"""
Simple test script for the TSA Item Checker API
Run this script to test the API locally or remotely
"""

import requests
import json
import sys

def test_api(base_url="http://localhost:8000"):
    """Test the TSA Item Checker API"""
    
    print(f"Testing API at: {base_url}")
    print("=" * 50)
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test items
    test_items = [
        "laptop",
        "shampoo 500ml",
        "knife",
        "water bottle",
        "phone charger",
        "scissors",
        "toothpaste"
    ]
    
    print("\nTesting POST /check-item:")
    print("-" * 30)
    
    for item in test_items:
        try:
            response = requests.post(
                f"{base_url}/check-item",
                json={"item": item},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {item}:")
                print(f"   Check-in: {data['check_in']}")
                print(f"   Carry-on: {data['carry_on']}")
                print(f"   Description: {data['description'][:100]}...")
                print()
            else:
                print(f"❌ {item}: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {item}: {e}")
    
    # Test GET endpoint
    print("\nTesting GET /check-item/{item}:")
    print("-" * 30)
    
    test_item = "sunscreen"
    try:
        response = requests.get(f"{base_url}/check-item/{test_item}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET {test_item}:")
            print(f"   Check-in: {data['check_in']}")
            print(f"   Carry-on: {data['carry_on']}")
            print(f"   Description: {data['description']}")
            if 'database_id' in data and data['database_id']:
                print(f"   Database ID: {data['database_id']}")
        else:
            print(f"❌ GET {test_item}: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ GET {test_item}: {e}")
    
    # Test stored responses endpoints
    print("\nTesting Supabase stored responses:")
    print("-" * 30)
    
    # Test getting all stored responses
    try:
        response = requests.get(f"{base_url}/stored-responses?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stored responses: {data['count']} found")
            for resp in data['responses'][:3]:  # Show first 3
                print(f"   - {resp['item']}: Check-in={resp['check_in']}, Carry-on={resp['carry_on']}")
        else:
            print(f"❌ Stored responses: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Stored responses: {e}")
    
    # Test getting responses for specific item
    try:
        response = requests.get(f"{base_url}/stored-responses/laptop")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Laptop responses: {data['count']} found")
        else:
            print(f"❌ Laptop responses: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Laptop responses: {e}")

if __name__ == "__main__":
    # Default to localhost, but allow URL as command line argument
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_api(url)