#!/usr/bin/env python3
"""
PostgreSQL Setup Script for MultiToolAPI
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

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL detected: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not found. Please install PostgreSQL first")
        return False

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
    directories = ["data/chroma_db", "uploads", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_postgresql_database():
    """Setup PostgreSQL database"""
    print("🗄️  Setting up PostgreSQL database...")
    
    try:
        # Test connection
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            database="multitoolapi",
            user="hasnainayazmacbook"
        )
        conn.close()
        print("✅ Database 'multitoolapi' is accessible")
        
        # Create tables using SQLAlchemy
        from app.core.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up PostgreSQL database: {e}")
        print("Please ensure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'multitoolapi' exists")
        print("  3. User has proper permissions")
        return False

def update_config_for_postgresql():
    """Update configuration to use PostgreSQL"""
    print("⚙️  Updating configuration for PostgreSQL...")
    
    # Update the database configuration
    config_file = Path("app/core/config.py")
    if config_file.exists():
        content = config_file.read_text()
        
        # Replace SQLite URL with PostgreSQL
        content = content.replace(
            'database_url: str = "sqlite:///./data/sqlite/multitoolapi.db"',
            'database_url: str = "postgresql://hasnainayazmacbook@localhost:5432/multitoolapi"'
        )
        
        config_file.write_text(content)
        print("✅ Configuration updated for PostgreSQL")
    
    # Create .env file from PostgreSQL template
    env_file = Path(".env")
    if not env_file.exists():
        postgresql_env = Path("env.postgresql")
        if postgresql_env.exists():
            env_file.write_text(postgresql_env.read_text())
            print("✅ Created .env file from PostgreSQL template")
        else:
            print("⚠️  PostgreSQL environment template not found")

def test_postgresql_setup():
    """Test the PostgreSQL setup"""
    print("🧪 Testing PostgreSQL setup...")
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, "test_postgresql.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL setup test passed")
            return True
        else:
            print(f"❌ PostgreSQL setup test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running PostgreSQL test: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 MultiToolAPI PostgreSQL Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check PostgreSQL
    if not check_postgresql():
        print("\n📋 To install PostgreSQL on macOS:")
        print("   brew install postgresql@16")
        print("   brew services start postgresql@16")
        print("   createdb multitoolapi")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Update configuration
    update_config_for_postgresql()
    
    # Setup PostgreSQL database
    if not setup_postgresql_database():
        sys.exit(1)
    
    # Test setup
    if not test_postgresql_setup():
        print("⚠️  Setup completed but tests failed")
        print("   You may need to check your PostgreSQL configuration")
    
    print("=" * 50)
    print("🎉 PostgreSQL setup completed successfully!")
    print()
    print("📝 Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python start_postgresql.py")
    print("3. Visit: http://localhost:8000/docs")
    print()
    print("🔑 Required API keys:")
    print("   - GEMINI_API_KEY (required)")
    print("   - GOOGLE_API_KEY (optional but recommended)")
    print()
    print("🗄️  Database:")
    print("   - Host: localhost")
    print("   - Database: multitoolapi")
    print("   - User: hasnainayazmacbook")
    print("=" * 50)

if __name__ == "__main__":
    main()
