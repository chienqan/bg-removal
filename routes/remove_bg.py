import io
from flask import Blueprint, request, send_file, jsonify
from PIL import Image
from utils.image_utils import get_input_image
from models.bg_remover import remove

remove_bg_bp = Blueprint("remove_bg", __name__)

@remove_bg_bp.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:
        # Get input image from request
        original_image = get_input_image(request)
        
        # Process the image with the background removal function
        output_image = remove(original_image)

        # Return the output as a PNG with transparency
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png", as_attachment=False, download_name="output.png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500