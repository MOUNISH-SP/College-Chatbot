#!/usr/bin/env python3
"""
PythonAnywhere WSGI Configuration File
======================================

This file configures your Flask app to run on PythonAnywhere
Replace 'yourusername' with your actual PythonAnywhere username
"""

import sys
import os

# Add your project directory to the Python path
project_home = '/home/yourusername/College-Chatbot'  # IMPORTANT: Replace 'yourusername' with your actual username
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import your Flask app
from app import app as application

# Set environment variables (you can also set these in the PythonAnywhere web interface)
os.environ['FLASK_ENV'] = 'production'

# Make sure the app is ready for deployment
if __name__ == "__main__":
    application.run()
