"""
Fixed Authentication Database Module
====================================

Handles MongoDB connection with proper error handling and fallback to file storage.
"""

import os
import json
import bcrypt
from datetime import datetime
from pathlib import Path

class AuthDB:
    def __init__(self):
        # Try MongoDB first, fallback to file storage
        self.use_mongodb = False
        self.users_file = Path("users.json")
        self.init_storage()
    
    def init_storage(self):
        """Initialize storage system"""
        try:
            # Try MongoDB connection
            from pymongo import MongoClient
            mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/kongu_chatbot")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.server_info()
            
            # Extract database name from URI or use default
            if "/" in mongo_uri.split("://")[-1]:
                db_name = mongo_uri.split("/")[-1].split("?")[0]
            else:
                db_name = "kongu_chatbot"
            
            self.db = self.client[db_name]
            self.users_collection = self.db["users"]
            self.use_mongodb = True
            print(f"✅ MongoDB connected successfully to database: {db_name}")
            
            # Create indexes for better performance
            self.users_collection.create_index("email", unique=True)
            self.users_collection.create_index("username", unique=True)
            
        except Exception as e:
            print(f"⚠️ MongoDB not available: {str(e)}")
            print("🔄 Using file-based storage instead")
            self.use_file_storage()
    
    def use_file_storage(self):
        """Initialize file-based storage as fallback"""
        if not self.users_file.exists():
            with open(self.users_file, 'w') as f:
                json.dump({"users": []}, f)
        self.use_mongodb = False
    
    def load_users_from_file(self):
        """Load users from JSON file"""
        try:
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                return data.get("users", [])
        except:
            return []
    
    def save_users_to_file(self, users):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump({"users": users}, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, password, hashed):
        """Verify password against hashed version"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    def create_user(self, username, email, password, full_name=""):
        """Create a new user"""
        try:
            # Check if user already exists
            if self.get_user_by_email(email):
                return False, "Email already registered"
            
            if self.get_user_by_username(username):
                return False, "Username already taken"
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user document
            user = {
                "id": str(datetime.utcnow().timestamp()),
                "username": username,
                "email": email,
                "password": hashed_password.decode('utf-8'),  # Store as string for JSON
                "full_name": full_name,
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True,
                "last_login": None
            }
            
            if self.use_mongodb:
                # Use MongoDB
                result = self.users_collection.insert_one(user)
                user["_id"] = result.inserted_id
                print(f"✅ User created in MongoDB: {username}")
                return True, "User created successfully"
            else:
                # Use file storage
                users = self.load_users_from_file()
                users.append(user)
                if self.save_users_to_file(users):
                    print(f"✅ User created in file storage: {username}")
                    return True, "User created successfully"
                else:
                    return False, "Error saving user data"
            
        except Exception as e:
            print(f"Error creating user: {e}")
            return False, f"Error creating user: {str(e)}"
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            if self.use_mongodb:
                user = self.users_collection.find_one({"email": email})
                return user
            else:
                users = self.load_users_from_file()
                for user in users:
                    if user.get("email") == email:
                        return user
                return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            if self.use_mongodb:
                user = self.users_collection.find_one({"username": username})
                return user
            else:
                users = self.load_users_from_file()
                for user in users:
                    if user.get("username") == username:
                        return user
                return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        try:
            user = self.get_user_by_email(email)
            
            if not user:
                return False, None, "User not found"
            
            if not user.get("is_active", True):
                return False, None, "Account is deactivated"
            
            # Convert password back to bytes if needed
            stored_password = user["password"]
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            
            if not self.verify_password(password, stored_password):
                return False, None, "Invalid password"
            
            # Update last login
            if self.use_mongodb:
                self.users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
            else:
                # Update in file storage
                users = self.load_users_from_file()
                for i, u in enumerate(users):
                    if u.get("email") == email:
                        users[i]["last_login"] = datetime.utcnow().isoformat()
                        self.save_users_to_file(users)
                        break
            
            # Remove password from user data before returning
            user_data = {
                "id": user.get("id", str(user.get("_id", ""))),
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "created_at": user.get("created_at"),
                "last_login": datetime.utcnow().isoformat()
            }
            
            print(f"✅ User authenticated: {email}")
            return True, user_data, "Login successful"
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, None, f"Authentication error: {str(e)}"
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            if self.use_mongodb:
                from bson.objectid import ObjectId
                user = self.users_collection.find_one({"_id": ObjectId(user_id)})
                if user:
                    return {
                        "id": str(user["_id"]),
                        "username": user["username"],
                        "email": user["email"],
                        "full_name": user.get("full_name", ""),
                        "created_at": user["created_at"],
                        "last_login": user.get("last_login")
                    }
            else:
                users = self.load_users_from_file()
                for user in users:
                    if user.get("id") == user_id:
                        return {
                            "id": user.get("id"),
                            "username": user["username"],
                            "email": user["email"],
                            "full_name": user.get("full_name", ""),
                            "created_at": user.get("created_at"),
                            "last_login": user.get("last_login")
                        }
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def update_user_profile(self, user_id, full_name=None):
        """Update user profile"""
        try:
            update_data = {}
            if full_name:
                update_data["full_name"] = full_name
            
            if not update_data:
                return False, "No updates provided"
            
            if self.use_mongodb:
                from bson.objectid import ObjectId
                self.users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
            else:
                users = self.load_users_from_file()
                for i, user in enumerate(users):
                    if user.get("id") == user_id:
                        users[i].update(update_data)
                        self.save_users_to_file(users)
                        break
            
            print(f"✅ Profile updated for user: {user_id}")
            return True, "Profile updated successfully"
            
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False, f"Error updating profile: {str(e)}"
    
    def get_all_users(self):
        """Get all users (for debugging)"""
        try:
            if self.use_mongodb:
                users = list(self.users_collection.find({}))
                return [{"username": u["username"], "email": u["email"]} for u in users]
            else:
                users = self.load_users_from_file()
                return [{"username": u["username"], "email": u["email"]} for u in users]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.use_mongodb and hasattr(self, 'client'):
            self.client.close()

# Global instance
auth_db = AuthDB()

# Test the connection
print(f"🔧 Auth system initialized with: {'MongoDB' if auth_db.use_mongodb else 'File Storage'}")
print(f"📊 Total users in system: {len(auth_db.get_all_users())}")
