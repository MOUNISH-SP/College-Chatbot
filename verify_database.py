"""
Verify Database Storage
========================

Verify that user data is being stored in your specific MongoDB database.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

def verify_database_storage():
    """Verify that data is stored in the correct database"""
    print("🔍 Verifying Database Storage...")
    
    # Get MongoDB URI
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/kongu_chatbot")
    print(f"📍 MongoDB URI: {mongo_uri}")
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Extract database name
        if "/" in mongo_uri.split("://")[-1]:
            db_name = mongo_uri.split("/")[-1].split("?")[0]
        else:
            db_name = "kongu_chatbot"
        
        print(f"🗄️ Database: {db_name}")
        
        # Access database
        db = client[db_name]
        
        # List all collections in the database
        collections = db.list_collection_names()
        print(f"📋 Collections in {db_name}: {collections}")
        
        # Check users collection
        if "users" in collections:
            users_collection = db["users"]
            
            # Count users
            user_count = users_collection.count_documents({})
            print(f"👥 Total users in database: {user_count}")
            
            # Show all users
            print("\n📊 Users stored in database:")
            users = users_collection.find({})
            for user in users:
                print(f"   - Username: {user.get('username', 'N/A')}")
                print(f"     Email: {user.get('email', 'N/A')}")
                print(f"     Full Name: {user.get('full_name', 'N/A')}")
                print(f"     Created: {user.get('created_at', 'N/A')}")
                print(f"     Last Login: {user.get('last_login', 'N/A')}")
                print(f"     ID: {user.get('_id', 'N/A')}")
                print()
            
            # Test adding a new user
            print("🧪 Testing new user creation...")
            test_user = {
                "username": f"test_user_{datetime.now().timestamp()}",
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "password": "hashed_password_here",
                "full_name": "Test User",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            result = users_collection.insert_one(test_user)
            print(f"✅ New user created with ID: {result.inserted_id}")
            
            # Verify the user was added
            new_count = users_collection.count_documents({})
            print(f"📊 New user count: {new_count}")
            
            # Clean up test user
            users_collection.delete_one({"_id": result.inserted_id})
            final_count = users_collection.count_documents({})
            print(f"🧹 After cleanup: {final_count} users")
            
        else:
            print("❌ No 'users' collection found in database")
        
        # Show database stats
        print(f"\n📈 Database Statistics:")
        stats = db.command("dbStats")
        print(f"   Collections: {stats.get('collections', 0)}")
        print(f"   Data Size: {stats.get('dataSize', 0)} bytes")
        print(f"   Storage Size: {stats.get('storageSize', 0)} bytes")
        
        client.close()
        print(f"\n🎉 Database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database verification FAILED!")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        return False

def show_connection_info():
    """Show connection information for user"""
    print("\n📋 Connection Information:")
    print("Your MongoDB connection is configured to:")
    print("   • Host: localhost")
    print("   • Port: 27017") 
    print("   • Database: kongu_chatbot")
    print("   • Collection: users")
    print("\n💡 All user signup/login data will be stored here!")

if __name__ == "__main__":
    success = verify_database_storage()
    show_connection_info()
    
    if success:
        print("\n✅ Your database is ready to store user data!")
        print("🚀 You can now test signup and login in your application!")
    else:
        print("\n❌ Please check your MongoDB connection and try again.")
