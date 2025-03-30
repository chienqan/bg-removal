#!/usr/bin/env python3
"""
Background Removal Server - Flask application for removing backgrounds from images.

This server provides a REST API for background removal using the BiRefNet model
and custom sky detection algorithms.

To run the server:
    python app.py [--port PORT] [--host HOST] [--debug]
"""

import os
import sys
import argparse
import logging
import time
import uuid
import json
from datetime import datetime
from flask import Flask, request, g
from flask_cors import CORS
from dotenv import load_dotenv
import warnings

# Load environment variables from .env file if present
load_dotenv()

# Filter out FutureWarnings to suppress timm deprecation warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def setup_production_logging(app):
    """Configure enhanced logging specifically for production environment"""
    # Create request logger
    request_logger = logging.getLogger('request_logger')
    # Clear any existing handlers to avoid duplicates
    if request_logger.handlers:
        request_logger.handlers = []
    request_logger.setLevel(logging.INFO)
    
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Create a file handler for API requests specifically
    api_log_file = os.path.join('logs', 'api_requests.log')
    file_handler = logging.FileHandler(api_log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    request_logger.addHandler(file_handler)
    
    # Also log to stdout in production for container environments
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(file_formatter)
    request_logger.addHandler(stdout_handler)
    
    app.logger.info(f"Production request logging enabled → logs/api_requests.log")
    return request_logger

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Determine if we're in production mode
    is_production = os.environ.get('FLASK_ENV', '').lower() == 'production'
    app.config['IS_PRODUCTION'] = is_production
    
    # Set up request logger - production has enhanced logging
    if is_production:
        request_logger = setup_production_logging(app)
        app.config['REQUEST_LOGGER'] = request_logger
        app.logger.info("Running in PRODUCTION mode with enhanced request logging")
    else:
        app.logger.info("Running in DEVELOPMENT mode")
   
    app.logger.info("Initializing Background Removal Server...")
    
    # Add request ID and start time to each request - only in production
    @app.before_request
    def before_request():
        # Always set request ID and timing info for use in route handlers
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        g.request_timestamp = datetime.utcnow().isoformat()
        
        # But only log in production mode
        if app.config.get('IS_PRODUCTION', False):
            app.logger.debug(f"[{g.request_id}] Request started: {request.method} {request.path} from {request.remote_addr}")
    
    # Log all requests - only in production
    @app.after_request
    def after_request(response):
        # Skip if not in production mode
        if not app.config.get('IS_PRODUCTION', False):
            return response
            
        # Skip logging for OPTIONS requests (CORS preflight)
        if request.method != 'OPTIONS':
            # Calculate processing time
            duration = time.time() - g.start_time
            
            # Determine input type and size
            input_type = None
            input_size = None
            if request.files and 'image_file' in request.files:
                input_type = 'file_upload'
                input_size = len(request.files['image_file'].read()) if request.files['image_file'] else 0
                # Reset file pointer after reading
                if request.files['image_file']:
                    request.files['image_file'].seek(0)
            elif 'image_url' in request.form:
                input_type = 'url'
                input_size = len(request.form['image_url'])
            elif 'image_file_b64' in request.form:
                input_type = 'base64'
                input_size = len(request.form['image_file_b64'])
            
            # Create a log entry with all important information
            log_data = {
                'request_id': g.request_id,
                'timestamp': g.request_timestamp,
                'remote_addr': request.remote_addr,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': f"{duration:.4f}s",
                'user_agent': request.headers.get('User-Agent', ''),
                'input_type': input_type,
                'input_size': input_size,
                'referrer': request.referrer,
                'content_length': response.content_length
            }
            
            # Log to the dedicated request logger
            if hasattr(app.config, 'REQUEST_LOGGER'):
                app.config['REQUEST_LOGGER'].info(json.dumps(log_data))
            
            # Also log a summary to the standard Flask logger
            app.logger.info(f"Request {g.request_id}: {request.method} {request.path} {response.status_code} - {duration:.4f}s")
            
        return response
    
    # Load model
    try:
        from models.birefnet_model import birefnet_model
        if birefnet_model is not None:
            app.logger.info("✅ BiRefNet model loaded successfully")
        else:
            app.logger.warning("⚠️ BiRefNet model could not be loaded, will use fallback method")
    except Exception as e:
        app.logger.error(f"❌ Error loading BiRefNet model: {str(e)}")
        app.logger.warning("⚠️ Will use fallback method for background removal")
    
    # Register blueprints
    from routes import register_routes
    register_routes(app)
    
    app.logger.info("✅ Server initialization complete")
    
    return app

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Background Removal Server")
    
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)),
                        help="Port to run the server on (default: 5000 or PORT env var)")
    parser.add_argument("--host", type=str, default=os.environ.get("HOST", "0.0.0.0"),
                        help="Host to bind the server to (default: 0.0.0.0 or HOST env var)")
    parser.add_argument("--debug", action="store_true",
                        help="Run server in debug mode")
    parser.add_argument("--log-level", type=str, default=os.environ.get("LOG_LEVEL", "INFO"),
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set logging level (default: INFO)")
    parser.add_argument("--production", action="store_true",
                        help="Run server in production mode with enhanced logging")
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Set logging level from arguments
    os.environ["LOG_LEVEL"] = args.log_level
    
    # Set environment based on arguments
    if args.production:
        os.environ["FLASK_ENV"] = "production"
    
    # Create the Flask app
    app = create_app()
    
    # Print startup message
    is_production = os.environ.get('FLASK_ENV', '').lower() == 'production'
    print(f"""
    ======================================================
    📷 Background Removal Server
    ======================================================
    🌐 Server running at: http://{args.host}:{args.port}
    🔧 Debug mode: {'✅ Enabled' if args.debug else '❌ Disabled'}
    🌍 Environment: {'🏭 PRODUCTION' if is_production else '🧪 DEVELOPMENT'}
    📋 Log level: {os.environ.get('LOG_LEVEL', 'INFO')}
    📊 API Request logging: {'✅ Enhanced (logs/api_requests.log)' if is_production else '❌ Disabled'}
    🛠️  Press Ctrl+C to stop the server
    ======================================================
    """)
    
    # Run the server
    app.run(host=args.host, port=args.port, debug=args.debug)

# Create 'app' variable for Gunicorn/PM2
app = create_app()