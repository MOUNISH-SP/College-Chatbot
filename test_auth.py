"""
Test Authentication System
===========================

Test the fixed authentication system to verify it's working correctly.
"""

from auth_db_fixed import auth_db

def test_authentication():
    """Test the authentication system"""
    print("🔍 Testing Authentication System...")
    
    # Show current users
    users = auth_db.get_all_users()
    print(f"\n📊 Current users in system: {len(users)}")
    for user in users:
        print(f"   - {user['username']} ({user['email']})")
    
    # Test user creation
    print("\n🧪 Testing user creation...")
    success, message = auth_db.create_user(
        username="testuser",
        email="test@example.com", 
        password="test123",
        full_name="Test User"
    )
    print(f"   Result: {success} - {message}")
    
    # Test authentication
    print("\n🔐 Testing authentication...")
    success, user_data, message = auth_db.authenticate_user("test@example.com", "test123")
    if success:
        print(f"   ✅ Login successful!")
        print(f"   User: {user_data['username']} ({user_data['email']})")
    else:
        print(f"   ❌ Login failed: {message}")
    
    # Test wrong password
    print("\n❌ Testing wrong password...")
    success, user_data, message = auth_db.authenticate_user("test@example.com", "wrongpass")
    print(f"   Result: {success} - {message}")
    
    # Show final user count
    users = auth_db.get_all_users()
    print(f"\n📊 Final user count: {len(users)}")
    
    print("\n🎉 Authentication test completed!")

if __name__ == "__main__":
    test_authentication()
