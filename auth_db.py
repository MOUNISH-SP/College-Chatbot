"""
Authentication Database Module
===============================

Handles MongoDB connection and user authentication operations.
"""

import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt

class AuthDB:
    def __init__(self):
        # MongoDB connection - using MongoDB Atlas (free cloud)
        # You can change this to your local MongoDB if needed
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client["kongu_chatbot"]
        self.users_collection = self.db["users"]
        
        # Create indexes for better performance
        self.users_collection.create_index("email", unique=True)
        self.users_collection.create_index("username", unique=True)
    
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
            if self.users_collection.find_one({"email": email}):
                return False, "Email already registered"
            
            if self.users_collection.find_one({"username": username}):
                return False, "Username already taken"
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user document
            user = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "full_name": full_name,
                "created_at": datetime.utcnow(),
                "is_active": True,
                "last_login": None
            }
            
            # Insert user
            result = self.users_collection.insert_one(user)
            return True, "User created successfully"
            
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        try:
            user = self.users_collection.find_one({"email": email})
            
            if not user:
                return False, None, "User not found"
            
            if not user["is_active"]:
                return False, None, "Account is deactivated"
            
            if not self.verify_password(password, user["password"]):
                return False, None, "Invalid password"
            
            # Update last login
            self.users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Remove password from user data before returning
            user_data = {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "created_at": user["created_at"],
                "last_login": datetime.utcnow()
            }
            
            return True, user_data, "Login successful"
            
        except Exception as e:
            return False, None, f"Authentication error: {str(e)}"
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
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
            return None
        except Exception:
            return None
    
    def update_user_profile(self, user_id, full_name=None):
        """Update user profile"""
        try:
            update_data = {}
            if full_name:
                update_data["full_name"] = full_name
            
            if update_data:
                self.users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
                return True, "Profile updated successfully"
            
            return False, "No updates provided"
            
        except Exception as e:
            return False, f"Error updating profile: {str(e)}"
    
    def close_connection(self):
        """Close MongoDB connection"""
        self.client.close()

# Global instance
auth_db = AuthDB()
