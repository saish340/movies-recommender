from flask import Flask, jsonify
import sys
import os
import json
import logging
import traceback
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app from main module
try:
    from main import app as flask_app
    logger.info("Successfully imported Flask app from main.py")
except Exception as e:
    logger.error(f"Error importing Flask app: {str(e)}")
    traceback.print_exc()
    # Create a minimal Flask app if main import fails
    flask_app = Flask(__name__)
    
    @flask_app.route('/')
    def error_home():
        return jsonify({"error": "Application failed to load"}), 500

# Vercel serverless function handler
def handler(request):
    """
    This is the main entry point for the Vercel serverless function.
    It wraps the Flask app and handles any exceptions that might occur.
    """
    try:
        # Process the request with the Flask app
        return flask_app(request.environ, request.start_response)
    except Exception as e:
        # Log the error
        error_stream = StringIO()
        traceback.print_exc(file=error_stream)
        error_details = error_stream.getvalue()
        logger.error(f"Unhandled error in Vercel handler: {str(e)}\n{error_details}")
        
        # Create a Flask response with error information
        response = jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        })
        response.status_code = 500
        return response(request.environ, request.start_response)