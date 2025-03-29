# routes/ping.py
from flask import Blueprint, jsonify
from models.birefnet_model import birefnet_model

ping_bp = Blueprint("ping", __name__)

@ping_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "API is running"})

@ping_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify model and API are running"""
    model_loaded = birefnet_model is not None
    return jsonify({
        "status": "healthy", 
        "model_loaded": model_loaded
    })