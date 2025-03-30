# routes/ping.py
from flask import Blueprint, jsonify, current_app
from models.birefnet_model import birefnet_model

ping_bp = Blueprint("ping", __name__)

@ping_bp.route("/ping", methods=["GET"])
def ping():
    current_app.logger.info(f"Ping request received")
    return jsonify({"message": "API is running"})

@ping_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify model and API are running"""
    current_app.logger.info(f"Health check request received")
    model_loaded = birefnet_model is not None
    current_app.logger.info(f"Health check: model_loaded={model_loaded}")
    return jsonify({
        "status": "healthy", 
        "model_loaded": model_loaded
    })