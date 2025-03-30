import io
import logging
import time
from flask import Blueprint, request, send_file, jsonify, current_app, g
from PIL import Image
from utils.image_utils import get_input_image
from models.bg_remover import remove

remove_bg_bp = Blueprint("remove_bg", __name__)

@remove_bg_bp.route("/remove-bg", methods=["POST"])
def remove_bg():
    # Always track timing
    start_process_time = time.time()
    
    try:
        # Always log request details
        input_method = ""
        if 'image_file' in request.files:
            input_method = "file_upload"
            current_app.logger.info(f"[{g.request_id}] Processing file upload")
        elif 'image_url' in request.form:
            input_method = "url"
            url = request.form['image_url']
            current_app.logger.info(f"[{g.request_id}] Processing URL: {url[:50]}..." if len(url) > 50 else f"[{g.request_id}] Processing URL: {url}")
        elif 'image_file_b64' in request.form:
            input_method = "base64"
            current_app.logger.info(f"[{g.request_id}] Processing base64 image ({len(request.form['image_file_b64'])//1024} KB)")
        else:
            current_app.logger.warning(f"[{g.request_id}] Invalid request: no image provided")
            return jsonify({"error": "No image provided"}), 400
            
        # Get input image from request
        image_load_start = time.time()
        original_image = get_input_image(request)
        image_load_time = time.time() - image_load_start
        
        current_app.logger.info(f"[{g.request_id}] Image loaded successfully: {original_image.size}, mode: {original_image.mode}, load_time: {image_load_time:.4f}s")
        
        # Process the image with the background removal function
        process_start = time.time()
        current_app.logger.info(f"[{g.request_id}] Starting background removal process")
        
        output_image = remove(original_image)
        process_time = time.time() - process_start
        
        current_app.logger.info(f"[{g.request_id}] Background removal completed in {process_time:.4f}s")

        # Return the output as a PNG with transparency
        buf = io.BytesIO()
        save_start = time.time()
        output_image.save(buf, format="PNG")
        save_time = time.time() - save_start
        buf.seek(0)
        
        total_time = time.time() - start_process_time
        current_app.logger.info(f"[{g.request_id}] Total processing time: {total_time:.4f}s (Load: {image_load_time:.4f}s, Process: {process_time:.4f}s, Save: {save_time:.4f}s)")
        current_app.logger.info(f"[{g.request_id}] Sending processed image to client (size: {output_image.size})")
        
        return send_file(buf, mimetype="image/png", as_attachment=False, download_name="output.png")

    except Exception as e:
        error_time = time.time() - start_process_time
        current_app.logger.error(f"[{g.request_id}] Error in background removal after {error_time:.4f}s: {str(e)}")
        import traceback
        current_app.logger.error(f"[{g.request_id}] Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500