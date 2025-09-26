#!/usr/bin/env python3
"""
Example usage of MultiToolAPI
This script demonstrates how to use the MultiToolAPI system
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def create_client_example():
    """Example: Create a new client"""
    print("🔹 Creating a new client...")
    
    client_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Example Corp",
        "website": "https://example.com",
        "phone": "+1-555-0123",
        "address": "123 Main St, New York, NY 10001",
        "industry": "Technology",
        "description": "A technology company focused on web development",
        "notes": "Interested in improving online presence and marketing"
    }
    
    response = requests.post(f"{BASE_URL}/clients/", json=client_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Client created successfully!")
        print(f"   Client ID: {result['client_id']}")
        print(f"   Name: {result['client']['name']}")
        return result['client_id']
    else:
        print(f"❌ Error creating client: {response.text}")
        return None

def upload_client_data_example(client_id: int):
    """Example: Upload client data"""
    print(f"🔹 Uploading data for client {client_id}...")
    
    # Example text data
    text_data = {
        "data_type": "notes",
        "title": "Client Requirements",
        "content": """
        The client wants to:
        1. Improve their website's SEO performance
        2. Increase online visibility
        3. Generate more leads through digital marketing
        4. Optimize their conversion rates
        5. Implement a content marketing strategy
        
        Current challenges:
        - Low organic traffic
        - Poor search engine rankings
        - Limited social media presence
        - Outdated website design
        - No clear call-to-actions
        """
    }
    
    response = requests.post(
        f"{BASE_URL}/clients/{client_id}/data",
        json=text_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Data uploaded successfully!")
        print(f"   Data ID: {result['data_id']}")
        print(f"   Processed: {result['processed']}")
    else:
        print(f"❌ Error uploading data: {response.text}")

def start_scraping_example(client_id: int):
    """Example: Start website scraping"""
    print(f"🔹 Starting website scraping for client {client_id}...")
    
    scraping_data = {
        "client_id": client_id,
        "url": "https://example.com",
        "scraping_type": "general",
        "strategy": "auto",
        "config": {
            "max_pages": 5,
            "follow_links": True,
            "extract_images": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/scraping/start", json=scraping_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Scraping job started!")
        print(f"   Job ID: {result['job_id']}")
        print(f"   Status: {result['status']}")
        return result['job_id']
    else:
        print(f"❌ Error starting scraping: {response.text}")
        return None

def query_rag_example(client_id: int):
    """Example: Query the RAG system"""
    print(f"🔹 Querying RAG system for client {client_id}...")
    
    query_data = {
        "client_id": client_id,
        "query": "What are the main challenges and opportunities for this business?",
        "k": 5
    }
    
    response = requests.post(f"{BASE_URL}/rag/query", json=query_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ RAG query completed!")
        print(f"   Question: {result['question']}")
        print(f"   Answer: {result['answer'][:200]}...")
        print(f"   Sources: {len(result['sources'])} documents found")
    else:
        print(f"❌ Error querying RAG: {response.text}")

def generate_solutions_example(client_id: int):
    """Example: Generate solutions"""
    print(f"🔹 Generating solutions for client {client_id}...")
    
    solution_data = {
        "client_id": client_id,
        "requirements": "Improve online presence and digital marketing",
        "goals": [
            "Increase organic traffic by 50%",
            "Improve search engine rankings",
            "Generate more qualified leads",
            "Enhance brand visibility"
        ],
        "priority_focus": "SEO and Content Marketing"
    }
    
    response = requests.post(f"{BASE_URL}/solutions/generate", json=solution_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Solution generation started!")
        print(f"   Client ID: {result['client_id']}")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Error generating solutions: {response.text}")

def get_analysis_example(client_id: int):
    """Example: Get marketing analysis"""
    print(f"🔹 Getting marketing analysis for client {client_id}...")
    
    response = requests.get(f"{BASE_URL}/analysis/marketing/{client_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Marketing analysis completed!")
        print(f"   Analysis type: Marketing Strategy")
        print(f"   Results: {json.dumps(result, indent=2)[:300]}...")
    else:
        print(f"❌ Error getting analysis: {response.text}")

def get_client_solutions_example(client_id: int):
    """Example: Get client solutions"""
    print(f"🔹 Getting solutions for client {client_id}...")
    
    response = requests.get(f"{BASE_URL}/solutions/{client_id}")
    
    if response.status_code == 200:
        solutions = response.json()
        print(f"✅ Found {len(solutions)} solutions!")
        for i, solution in enumerate(solutions[:3], 1):  # Show first 3
            print(f"   {i}. {solution['title']} ({solution['priority']} priority)")
    else:
        print(f"❌ Error getting solutions: {response.text}")

def main():
    """Main example function"""
    print("🚀 MultiToolAPI Usage Example")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ API is not running. Please start the server first:")
            print("   python start_simple.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please start the server first:")
        print("   python start_simple.py")
        return
    
    print("✅ API is running!")
    print()
    
    # Step 1: Create a client
    client_id = create_client_example()
    if not client_id:
        return
    
    print()
    
    # Step 2: Upload client data
    upload_client_data_example(client_id)
    print()
    
    # Step 3: Start website scraping
    job_id = start_scraping_example(client_id)
    if job_id:
        print("   ⏳ Waiting for scraping to complete...")
        time.sleep(5)  # Wait a bit for scraping to complete
    print()
    
    # Step 4: Query RAG system
    query_rag_example(client_id)
    print()
    
    # Step 5: Generate solutions
    generate_solutions_example(client_id)
    print()
    
    # Step 6: Get analysis
    get_analysis_example(client_id)
    print()
    
    # Step 7: Get solutions
    get_client_solutions_example(client_id)
    print()
    
    print("🎉 Example completed!")
    print("=" * 50)
    print("📚 Check the API documentation at: http://localhost:8000/docs")
    print("🔍 View all endpoints and try them interactively!")

if __name__ == "__main__":
    main()
