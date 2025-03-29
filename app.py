"""
Background Removal API Server

This server provides a REST API for removing backgrounds from images
using the BiRefNet model with preservation of natural elements.

Run with:
    python app.py
"""

import os
import logging
from flask import Flask
from routes import register_routes
from models.birefnet_model import birefnet_model  # Import to ensure model is loaded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory function to create and configure the Flask app"""
    # Initialize Flask app
    app = Flask(__name__)
    
    # Register all route blueprints
    register_routes(app)
    
    # Log that the app is initialized
    logger.info("Flask application initialized")
    
    # Verify model is loaded
    if birefnet_model is not None:
        logger.info("BiRefNet model loaded successfully")
    else:
        logger.error("BiRefNet model failed to load")
    
    return app

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Create the app
    app = create_app()
    
    # Run the server
    app.run(host='0.0.0.0', port=port, debug=False)
