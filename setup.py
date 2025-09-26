#!/usr/bin/env python3
"""
Setup script for MultiToolAPI (No Docker version)
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["data/chroma_db", "uploads", "logs", "data/sqlite"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_sqlite_database():
    """Setup SQLite database as an alternative to PostgreSQL"""
    print("🗄️  Setting up SQLite database...")
    
    db_path = "data/sqlite/multitoolapi.db"
    
    # Create database file
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables (simplified version)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            company TEXT,
            website TEXT,
            phone TEXT,
            address TEXT,
            industry TEXT,
            description TEXT,
            notes TEXT,
            metadata TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            data_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            file_path TEXT,
            file_type TEXT,
            file_size INTEGER,
            metadata TEXT,
            is_processed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            scraping_type TEXT DEFAULT 'general',
            config TEXT,
            result TEXT,
            error_message TEXT,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraped_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            page_url TEXT NOT NULL,
            page_title TEXT,
            content_type TEXT,
            content TEXT,
            metadata TEXT,
            is_processed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES scraping_jobs (id),
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            solution_type TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'draft',
            content TEXT NOT NULL,
            metadata TEXT,
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ SQLite database created at: {db_path}")
    return True

def update_config_for_sqlite():
    """Update configuration to use SQLite instead of PostgreSQL"""
    print("⚙️  Updating configuration for SQLite...")
    
    # Update the database configuration
    config_file = Path("app/core/config.py")
    if config_file.exists():
        content = config_file.read_text()
        
        # Replace PostgreSQL URL with SQLite
        content = content.replace(
            'database_url: str = "postgresql://username:password@localhost:5432/multitoolapi"',
            'database_url: str = "sqlite:///./data/sqlite/multitoolapi.db"'
        )
        
        config_file.write_text(content)
        print("✅ Configuration updated for SQLite")
    
    # Update .env.example
    env_file = Path("env.example")
    if env_file.exists():
        content = env_file.read_text()
        
        # Replace PostgreSQL URL with SQLite
        content = content.replace(
            'DATABASE_URL=postgresql://username:password@localhost:5432/multitoolapi',
            'DATABASE_URL=sqlite:///./data/sqlite/multitoolapi.db'
        )
        
        # Remove Redis requirement for simple setup
        content = content.replace(
            'REDIS_URL=redis://localhost:6379',
            '# REDIS_URL=redis://localhost:6379  # Optional for simple setup'
        )
        
        env_file.write_text(content)
        print("✅ Environment example updated for SQLite")

def create_simple_env():
    """Create a simple .env file with minimal configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        
        env_content = """# MultiToolAPI Configuration (Simple Setup)

# Database (SQLite - no setup required)
DATABASE_URL=sqlite:///./data/sqlite/multitoolapi.db

# Gemini AI (Required)
GEMINI_API_KEY=your_gemini_api_key_here

# Google APIs (Optional but recommended)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Vector Database
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Scraping Configuration
SCRAPING_DELAY=1
MAX_CONCURRENT_REQUESTS=5
USER_AGENT=MultiToolAPI/1.0

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIRECTORY=./uploads

# Application
DEBUG=true
PROJECT_NAME=MultiToolAPI
"""
        
        env_file.write_text(env_content)
        print("✅ .env file created")
        print("⚠️  Please edit .env file and add your API keys!")

def create_simple_start_script():
    """Create a simplified start script without Docker dependencies"""
    start_script = Path("start_simple.py")
    
    script_content = '''#!/usr/bin/env python3
"""
Simple startup script for MultiToolAPI (No Docker)
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import langchain
        import chromadb
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: python setup.py")
        return False

def check_environment():
    """Check environment configuration"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Please run: python setup.py")
        return False
    
    # Check for required environment variables
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == f"your_{var.lower()}_here":
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Please configure these in your .env file: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting MultiToolAPI (Simple Mode)...")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("⚠️  Please configure your .env file first")
        sys.exit(1)
    
    print("=" * 50)
    print("🎯 Starting FastAPI server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main_simple:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\\n👋 Shutting down MultiToolAPI...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    start_script.write_text(script_content)
    start_script.chmod(0o755)
    print("✅ Simple start script created: start_simple.py")

def main():
    """Main setup function"""
    print("🔧 MultiToolAPI Setup (No Docker)")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup SQLite database
    setup_sqlite_database()
    
    # Update configuration
    update_config_for_sqlite()
    
    # Create .env file
    create_simple_env()
    
    # Create simple start script
    create_simple_start_script()
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print()
    print("📝 Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python start_simple.py")
    print("3. Visit: http://localhost:8000/docs")
    print()
    print("🔑 Required API keys:")
    print("   - GEMINI_API_KEY (required)")
    print("   - GOOGLE_API_KEY (optional but recommended)")
    print("=" * 50)

if __name__ == "__main__":
    main()
