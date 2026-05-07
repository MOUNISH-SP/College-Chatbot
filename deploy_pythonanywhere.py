#!/usr/bin/env python3
"""
PythonAnywhere Deployment Script
================================
This script helps prepare and deploy your Flask app on PythonAnywhere
"""

import os
import sys

def create_requirements_for_pythonanywhere():
    """Create requirements.txt optimized for PythonAnywhere"""
    
    requirements = """Flask==2.3.3
Flask-WTF==1.1.1
Werkzeug==2.3.7
pymongo==4.5.0
python-dotenv==1.0.0
bcrypt==4.0.1
requests==2.31.0
pdfplumber==0.9.0
PyPDF2==3.0.1
python-docx==0.8.11
easyocr==1.7.0
Pillow==10.0.1
pinecone-client==2.2.4
openai==0.28.1
tqdm==4.66.1
markupsafe==2.1.3
"""
    
    with open('requirements_pythonanywhere.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements_pythonanywhere.txt")

def create_pythonanywhere_wsgi():
    """Create WSGI file for PythonAnywhere"""
    
    wsgi_content = """import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/College-Chatbot'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import your Flask app
from app import app as application

# Make sure the app is ready for deployment
if __name__ == "__main__":
    application.run()
"""
    
    with open('pythonanywhere_wsgi.py', 'w') as f:
        f.write(wsgi_content)
    
    print("✅ Created pythonanywhere_wsgi.py")

def create_deploy_instructions():
    """Create detailed deployment instructions"""
    
    instructions = """# PythonAnywhere Deployment Instructions

## 1. Upload Your Files
- Go to the PythonAnywhere Dashboard
- Click "Files" → "Upload a file"
- Upload all your project files to /home/yourusername/College-Chatbot/

## 2. Install Dependencies
- Go to "Consoles" → "Bash"
- Run: cd College-Chatbot
- Run: pip install -r requirements_pythonanywhere.txt

## 3. Set Up Environment Variables
- In your Bash console, run:
- export SARVAM_API_KEY="your_sarvam_api_key"
- export PINECONE_API_KEY="your_pinecone_api_key"
- export MONGODB_URI="mongodb://yourusername:yourpassword@yourusername.mongo.cosmos.azure.com:27017/college-chatbot?ssl=true&replicaSet=globaldb"

## 4. Configure Web App
- Go to "Web" → your web app
- Set "Source code" to: /home/yourusername/College-Chatbot
- Set "Working directory" to: /home/yourusername/College-Chatbot
- Set "WSGI configuration file" to: /home/yourusername/College-Chatbot/pythonanywhere_wsgi.py

## 5. Reload Web App
- Click the "Reload" button on your web app page
- Your app should be live at: http://yourusername.pythonanywhere.com

## 6. Test Your App
- Visit your URL and test all features
- Check file uploads, user registration, and chatbot functionality
"""
    
    with open('DEPLOY_PYTHONANYWHERE.md', 'w') as f:
        f.write(instructions)
    
    print("✅ Created DEPLOY_PYTHONANYWHERE.md")

def create_app_config_for_production():
    """Create production-ready app configuration"""
    
    config_content = """# Production Configuration for PythonAnywhere
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/kongu_chatbot')
    SARVAM_API_KEY = os.environ.get('SARVAM_API_KEY')
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
    
    # Upload folder configuration
    UPLOAD_FOLDER = '/home/yourusername/College-Chatbot/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Security settings
    DEBUG = False
    TESTING = False
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
"""
    
    with open('config_production.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Created config_production.py")

if __name__ == "__main__":
    print("🚀 Preparing your project for PythonAnywhere deployment...")
    
    create_requirements_for_pythonanywhere()
    create_pythonanywhere_wsgi()
    create_deploy_instructions()
    create_app_config_for_production()
    
    print("\n✅ Deployment files created successfully!")
    print("📋 Next steps:")
    print("1. Upload all files to PythonAnywhere")
    print("2. Follow DEPLOY_PYTHONANYWHERE.md instructions")
    print("3. Test your deployed application")
    print("\n🌐 Your app will be live at: http://yourusername.pythonanywhere.com")
"""
"""
PythonAnywhere WSGI Configuration
==================================

This file configures your Flask app to run on PythonAnywhere
"""

import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/mysite'  # Replace with your actual path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import your Flask app
from app import app as application

# Make sure the app is ready for deployment
if __name__ == "__main__":
    application.run()
