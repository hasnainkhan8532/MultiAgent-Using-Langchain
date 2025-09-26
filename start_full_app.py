#!/usr/bin/env python3
"""
Start both the MultiToolAPI backend and frontend
"""

import subprocess
import sys
import time
import webbrowser
import os
import signal
import threading
from pathlib import Path

def start_api():
    """Start the FastAPI backend"""
    print("🚀 Starting MultiToolAPI Backend...")
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
        
        # Start the API
        process = subprocess.Popen(
            [sys.executable, "app_simple.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting Frontend Server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "serve_frontend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def check_api_health():
    """Check if API is healthy"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🎯 MultiToolAPI - Full Application Startup")
    print("=" * 50)
    
    # Start API
    api_process = start_api()
    if not api_process:
        print("❌ Failed to start API")
        sys.exit(1)
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        if check_api_health():
            print("✅ API is ready!")
            break
        time.sleep(1)
    else:
        print("❌ API failed to start within 30 seconds")
        api_process.terminate()
        sys.exit(1)
    
    # Start Frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend")
        api_process.terminate()
        sys.exit(1)
    
    # Wait a moment for frontend to start
    time.sleep(2)
    
    print("\n🎉 MultiToolAPI is now running!")
    print("=" * 50)
    print("🔗 Frontend: http://localhost:3000")
    print("🔗 API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n💡 Press Ctrl+C to stop both servers")
    print("=" * 50)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass
    
    # Handle shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down MultiToolAPI...")
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
