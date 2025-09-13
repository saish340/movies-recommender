from flask import Flask, request
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from main.py
from main import app as flask_app

# This is the serverless function handler for Vercel
def handler(request):
    # Make request context available to Flask app
    with flask_app.request_context(request):
        return flask_app(request.environ, request.start_response)