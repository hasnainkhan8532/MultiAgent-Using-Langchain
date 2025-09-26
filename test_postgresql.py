#!/usr/bin/env python3
"""
PostgreSQL Database Test Script for MultiToolAPI
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.client import Client, ClientData
from app.models.scraping import ScrapingJob, ScrapedData
from app.models.solution import Solution
from app.core.database import Base

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    print("🔍 Testing PostgreSQL connection...")
    
    # Update database URL for PostgreSQL
    postgres_url = "postgresql://hasnainayazmacbook@localhost:5432/multitoolapi_test"
    
    try:
        engine = create_engine(postgres_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
            # Test database operations
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Database: {db_name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_tables():
    """Create database tables"""
    print("🔧 Creating database tables...")
    
    postgres_url = "postgresql://hasnainayazmacbook@localhost:5432/multitoolapi_test"
    
    try:
        engine = create_engine(postgres_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        return engine
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return None

def test_crud_operations(engine):
    """Test CRUD operations"""
    print("📝 Testing CRUD operations...")
    
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create a test client
        test_client = Client(
            name="Test Client",
            email="test@example.com",
            company="Test Company",
            website="https://test.com",
            industry="Technology",
            description="Test client for PostgreSQL testing"
        )
        
        db.add(test_client)
        db.commit()
        db.refresh(test_client)
        
        print(f"✅ Created client: {test_client.name} (ID: {test_client.id})")
        
        # Create test client data
        test_data = ClientData(
            client_id=test_client.id,
            data_type="notes",
            title="Test Data",
            content="This is test data for PostgreSQL testing",
            data_metadata={"test": True}
        )
        
        db.add(test_data)
        db.commit()
        db.refresh(test_data)
        
        print(f"✅ Created client data: {test_data.title} (ID: {test_data.id})")
        
        # Create test scraping job
        test_job = ScrapingJob(
            client_id=test_client.id,
            url="https://test.com",
            status="completed",
            scraping_type="test",
            result={"test": "data"}
        )
        
        db.add(test_job)
        db.commit()
        db.refresh(test_job)
        
        print(f"✅ Created scraping job: {test_job.url} (ID: {test_job.id})")
        
        # Create test solution
        test_solution = Solution(
            client_id=test_client.id,
            title="Test Solution",
            description="A test solution for PostgreSQL testing",
            solution_type="recommendation",
            content="This is a test solution",
            priority="high"
        )
        
        db.add(test_solution)
        db.commit()
        db.refresh(test_solution)
        
        print(f"✅ Created solution: {test_solution.title} (ID: {test_solution.id})")
        
        # Test queries
        clients = db.query(Client).all()
        print(f"✅ Found {len(clients)} clients")
        
        client_data = db.query(ClientData).all()
        print(f"✅ Found {len(client_data)} client data records")
        
        jobs = db.query(ScrapingJob).all()
        print(f"✅ Found {len(jobs)} scraping jobs")
        
        solutions = db.query(Solution).all()
        print(f"✅ Found {len(solutions)} solutions")
        
        # Clean up test data
        db.query(ClientData).filter(ClientData.client_id == test_client.id).delete()
        db.query(ScrapingJob).filter(ScrapingJob.client_id == test_client.id).delete()
        db.query(Solution).filter(Solution.client_id == test_client.id).delete()
        db.query(Client).filter(Client.id == test_client.id).delete()
        db.commit()
        
        print("✅ Test data cleaned up")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error in CRUD operations: {e}")
        return False

def test_foreign_keys(engine):
    """Test foreign key relationships"""
    print("🔗 Testing foreign key relationships...")
    
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create test client
        test_client = Client(
            name="FK Test Client",
            email="fk_test@example.com",
            company="FK Test Company"
        )
        
        db.add(test_client)
        db.commit()
        db.refresh(test_client)
        
        # Create related data
        test_data = ClientData(
            client_id=test_client.id,
            data_type="test",
            title="FK Test Data",
            content="Foreign key test data"
        )
        
        test_job = ScrapingJob(
            client_id=test_client.id,
            url="https://fk-test.com",
            status="pending"
        )
        
        test_solution = Solution(
            client_id=test_client.id,
            title="FK Test Solution",
            solution_type="test",
            content="Foreign key test solution"
        )
        
        db.add_all([test_data, test_job, test_solution])
        db.commit()
        
        # Test relationships
        client_with_data = db.query(Client).filter(Client.id == test_client.id).first()
        related_data = db.query(ClientData).filter(ClientData.client_id == test_client.id).all()
        related_jobs = db.query(ScrapingJob).filter(ScrapingJob.client_id == test_client.id).all()
        related_solutions = db.query(Solution).filter(Solution.client_id == test_client.id).all()
        
        print(f"✅ Client: {client_with_data.name}")
        print(f"✅ Related data records: {len(related_data)}")
        print(f"✅ Related jobs: {len(related_jobs)}")
        print(f"✅ Related solutions: {len(related_solutions)}")
        
        # Clean up
        db.query(ClientData).filter(ClientData.client_id == test_client.id).delete()
        db.query(ScrapingJob).filter(ScrapingJob.client_id == test_client.id).delete()
        db.query(Solution).filter(Solution.client_id == test_client.id).delete()
        db.query(Client).filter(Client.id == test_client.id).delete()
        db.commit()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing foreign keys: {e}")
        return False

def test_performance(engine):
    """Test database performance"""
    print("⚡ Testing database performance...")
    
    try:
        import time
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test insert performance
        start_time = time.time()
        
        clients = []
        for i in range(100):
            client = Client(
                name=f"Perf Test Client {i}",
                email=f"perf_test_{i}@example.com",
                company=f"Perf Test Company {i}"
            )
            clients.append(client)
        
        db.add_all(clients)
        db.commit()
        
        insert_time = time.time() - start_time
        print(f"✅ Inserted 100 clients in {insert_time:.3f} seconds")
        
        # Test query performance
        start_time = time.time()
        
        all_clients = db.query(Client).filter(Client.name.like("Perf Test Client %")).all()
        
        query_time = time.time() - start_time
        print(f"✅ Queried {len(all_clients)} clients in {query_time:.3f} seconds")
        
        # Test update performance
        start_time = time.time()
        
        for client in all_clients:
            client.description = "Updated description"
        
        db.commit()
        
        update_time = time.time() - start_time
        print(f"✅ Updated {len(all_clients)} clients in {update_time:.3f} seconds")
        
        # Clean up
        db.query(Client).filter(Client.name.like("Perf Test Client %")).delete()
        db.commit()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing performance: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 PostgreSQL Database Test for MultiToolAPI")
    print("=" * 60)
    
    # Test 1: Connection
    if not test_postgresql_connection():
        print("❌ Cannot proceed without database connection")
        return
    
    print()
    
    # Test 2: Create tables
    engine = create_tables()
    if not engine:
        print("❌ Cannot proceed without tables")
        return
    
    print()
    
    # Test 3: CRUD operations
    if not test_crud_operations(engine):
        print("❌ CRUD operations failed")
        return
    
    print()
    
    # Test 4: Foreign keys
    if not test_foreign_keys(engine):
        print("❌ Foreign key tests failed")
        return
    
    print()
    
    # Test 5: Performance
    if not test_performance(engine):
        print("❌ Performance tests failed")
        return
    
    print()
    print("🎉 All PostgreSQL tests passed!")
    print("=" * 60)
    print("✅ Database connection: OK")
    print("✅ Table creation: OK")
    print("✅ CRUD operations: OK")
    print("✅ Foreign keys: OK")
    print("✅ Performance: OK")
    print()
    print("🔧 To use PostgreSQL in your app:")
    print("   1. Update .env file with: DATABASE_URL=postgresql://hasnainayazmacbook@localhost:5432/multitoolapi_test")
    print("   2. Or create a new database: createdb multitoolapi")
    print("   3. Update the connection string accordingly")

if __name__ == "__main__":
    main()
