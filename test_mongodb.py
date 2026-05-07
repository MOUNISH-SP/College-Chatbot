"""
Test MongoDB Connection
========================

Testp-6pjp65k6hjjhkhkh script to diagnose MongoDB connection issues.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB Connection...")
    
    # Get MongoDB URI
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    print(f"📍 MongoDB URI: {mongo_uri}")
    
    try:
        # Test connection
        print("\n🔗 Testing connection...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test server info
        server_info = client.server_info()
        print(f"✅ Connected to MongoDB!")
        print(f"   Version: {server_info['version']}")
        print(f"   Host: {server_info['host']}")
        
        # Test database operations
        print("\n📊 Testing database operations...")
        db = client["kongu_chatbot_test"]
        test_collection = db["test_collection"]
        
        # Insert test document
        test_doc = {
            "test": "Hello MongoDB!",
            "timestamp": datetime.utcnow(),
            "success": True
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ Insert successful: {result.inserted_id}")
        
        # Find document
        found_doc = test_collection.find_one({"test": "Hello MongoDB!"})
        if found_doc:
            print(f"✅ Find successful: {found_doc['test']}")
        
        # Clean up
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
        # List databases
        print("\n📋 Available databases:")
        databases = client.list_database_names()
        for db_name in databases:
            print(f"   - {db_name}")
        
        client.close()
        print("\n🎉 MongoDB connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ MongoDB connection FAILED!")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        
        # Provide solutions
        print("\n🔧 Possible Solutions:")
        print("1. Install MongoDB Community Server")
        print("2. Start MongoDB service")
        print("3. Use MongoDB Atlas (cloud)")
        print("4. Check if MongoDB is running on port 27017")
        
        return False

def test_with_mongodb_atlas():
    """Test with MongoDB Atlas cloud service"""
    print("\n🌐 Testing MongoDB Atlas Alternative...")
    
    # Free MongoDB Atlas connection string (you'll need to create your own)
    atlas_uri = "mongodb+srv://username:password@cluster.mongodb.net/kongu_chatbot?retryWrites=true&w=majority"
    
    print("📝 To use MongoDB Atlas:")
    print("1. Create free account at https://www.mongodb.com/atlas")
    print("2. Create free cluster")
    print("3. Get connection string")
    print("4. Update MONGODB_URI in .env file")
    
    return False

if __name__ == "__main__":
    success = test_mongodb_connection()
    
    if not success:
        test_with_mongodb_atlas()
        
        print("\n🚀 Quick Fix Options:")
        print("Option 1: Install MongoDB locally")
        print("   - Download: https://www.mongodb.com/try/download/community")
        print("   - Install and start MongoDB service")
        
        print("\nOption 2: Use MongoDB Atlas (Recommended)")
        print("   - Free cloud MongoDB")
        print("   - No installation required")
        print("   - Works from anywhere")
