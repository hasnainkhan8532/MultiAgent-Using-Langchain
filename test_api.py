#!/usr/bin/env python3
"""
Test script for MultiToolAPI
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_client():
    """Test client creation"""
    print("👤 Testing client creation...")
    client_data = {
        "name": "Jane Smith",
        "email": "jane@techcorp.com",
        "company": "TechCorp Solutions",
        "website": "https://techcorp.com",
        "industry": "Software Development",
        "description": "A leading software development company"
    }
    
    response = requests.post(f"{BASE_URL}/clients/", json=client_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_clients():
    """Test getting all clients"""
    print("📋 Testing get all clients...")
    response = requests.get(f"{BASE_URL}/clients/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_scrape_website():
    """Test website scraping"""
    print("🌐 Testing website scraping...")
    scraping_data = {
        "url": "https://httpbin.org/html",
        "strategy": "requests"
    }
    
    response = requests.post(f"{BASE_URL}/scraping/scrape", json=scraping_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Message: {result['message']}")
    print(f"Title: {result['data']['title']}")
    print(f"Headings: {result['data']['headings']}")
    print()

def test_get_scraped_data():
    """Test getting scraped data"""
    print("📊 Testing get scraped data...")
    response = requests.get(f"{BASE_URL}/scraping/data")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Scraped data count: {len(result['scraped_data'])}")
    print()

def test_system_status():
    """Test system status"""
    print("⚙️ Testing system status...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def main():
    """Main test function"""
    print("🚀 MultiToolAPI Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_create_client()
        test_get_clients()
        test_scrape_website()
        test_get_scraped_data()
        test_system_status()
        
        print("🎉 All tests completed successfully!")
        print("=" * 50)
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running:")
        print("   python app_simple.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
