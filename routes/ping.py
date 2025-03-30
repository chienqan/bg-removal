# routes/ping.py
from flask import Blueprint, jsonify, current_app, g
from models.birefnet_model import birefnet_model

ping_bp = Blueprint("ping", __name__)

@ping_bp.route("/ping", methods=["GET"])
def ping():
    # Always log ping requests
    current_app.logger.info(f"[{g.request_id}] Ping request received")
    return jsonify({"message": "API is running"})

@ping_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify model and API are running"""
    model_loaded = birefnet_model is not None
    
    # Always log health check requests
    current_app.logger.info(f"[{g.request_id}] Health check request received")
    current_app.logger.info(f"[{g.request_id}] Health check: model_loaded={model_loaded}")
    
    return jsonify({
        "status": "healthy", 
        "model_loaded": model_loaded
    })