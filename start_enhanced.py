#!/usr/bin/env python3
"""
Start the Enhanced MultiToolAPI with client-centric features
"""

import subprocess
import sys
import time
import webbrowser
import os
import signal
import threading
from pathlib import Path

def start_enhanced_api():
    """Start the Enhanced FastAPI backend"""
    print("🚀 Starting Enhanced MultiToolAPI Backend...")
    try:
        # Load environment variables
        env = os.environ.copy()
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value
        
        # Start the Enhanced API
        process = subprocess.Popen(
            [sys.executable, "app_enhanced.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Error starting Enhanced API: {e}")
        return None

def start_enhanced_frontend():
    """Start the enhanced frontend server"""
    print("🌐 Starting Enhanced Frontend Server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "http.server", "3000", "--directory", "frontend_enhanced"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Error starting enhanced frontend: {e}")
        return None

def check_api_health():
    """Check if Enhanced API is healthy"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎯 MultiToolAPI - Enhanced Client-Centric System")
    print("=" * 60)
    print("🔧 Features:")
    print("   • Client-centric data alignment")
    print("   • Web scraping per client")
    print("   • RAG system for knowledge management")
    print("   • Google Maps API integration")
    print("   • Intelligent AI chatbot")
    print("   • Comprehensive dashboard")
    print("=" * 60)
    
    # Start Enhanced API
    api_process = start_enhanced_api()
    if not api_process:
        print("❌ Failed to start Enhanced API")
        sys.exit(1)
    
    # Wait for API to be ready
    print("⏳ Waiting for Enhanced API to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        if check_api_health():
            print("✅ Enhanced API is ready!")
            break
        time.sleep(1)
    else:
        print("❌ Enhanced API failed to start within 30 seconds")
        api_process.terminate()
        sys.exit(1)
    
    # Start Enhanced Frontend
    frontend_process = start_enhanced_frontend()
    if not frontend_process:
        print("❌ Failed to start enhanced frontend")
        api_process.terminate()
        sys.exit(1)
    
    # Wait a moment for frontend to start
    time.sleep(2)
    
    print("\n🎉 Enhanced MultiToolAPI is now running!")
    print("=" * 60)
    print("🔗 Enhanced Frontend: http://localhost:3000")
    print("🔗 Enhanced API: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n💡 Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass
    
    # Handle shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down Enhanced MultiToolAPI...")
        if api_process:
            api_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("👋 Goodbye!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
