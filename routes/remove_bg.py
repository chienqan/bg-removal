import io
import logging
from flask import Blueprint, request, send_file, jsonify, current_app
from PIL import Image
from utils.image_utils import get_input_image
from models.bg_remover import remove

remove_bg_bp = Blueprint("remove_bg", __name__)

@remove_bg_bp.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:
        # Log request details
        current_app.logger.info(f"Background removal request received from {request.remote_addr}")
        
        if 'image_file' in request.files:
            current_app.logger.info("Processing file upload")
        elif 'image_url' in request.form:
            current_app.logger.info(f"Processing URL: {request.form['image_url']}")
        elif 'image_file_b64' in request.form:
            current_app.logger.info("Processing base64 image")
        else:
            current_app.logger.warning("Invalid request: no image provided")
            return jsonify({"error": "No image provided"}), 400
            
        # Get input image from request
        original_image = get_input_image(request)
        current_app.logger.info(f"Image loaded successfully: {original_image.size}")
        
        # Process the image with the background removal function
        current_app.logger.info("Starting background removal process")
        output_image = remove(original_image)
        current_app.logger.info("Background removal completed successfully")

        # Return the output as a PNG with transparency
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        buf.seek(0)
        current_app.logger.info("Sending processed image to client")
        return send_file(buf, mimetype="image/png", as_attachment=False, download_name="output.png")

    except Exception as e:
        current_app.logger.error(f"Error in background removal: {str(e)}")
        return jsonify({"error": str(e)}), 500