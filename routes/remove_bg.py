import io
import base64
import requests
from flask import Blueprint, request, send_file, jsonify
from PIL import Image
from torchvision import transforms
import torch
from models.birefnet_model import birefnet_model
from config import DEVICE, MODEL_INPUT_SIZE
from utils.param_utils import compute_target_size, get_output_format
from utils.image_utils import get_input_image

remove_bg_bp = Blueprint("remove_bg", __name__)
to_pil = transforms.ToPILImage()

@remove_bg_bp.route("/remove-bg", methods=["POST"])
def remove_bg():
    try:
        # Get input image from request
        original_image = get_input_image(request)
        orig_size = original_image.size

        # Get "size" and "format" parameters from form-data
        size_param = request.form.get("size")  # No default
        fmt_param = request.form.get("format")   # No default

        # Calculate target size based on original image and size parameter
        target_size = compute_target_size(orig_size, size_param) if size_param else None
        # Output format: defaults to "png" if not provided
        out_format = get_output_format(fmt_param) if fmt_param else "png"

        # Convert image for model: resize to MODEL_INPUT_SIZE, convert to tensor and normalize
        transform_image = transforms.Compose([
            transforms.Resize(MODEL_INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
        input_tensor = transform_image(original_image).unsqueeze(0).to(DEVICE)
        if DEVICE.type == "cuda":
            input_tensor = input_tensor.half()

        # Call model, get final output and apply sigmoid to get mask from 0 to 1
        with torch.no_grad():
            preds = birefnet_model(input_tensor)[-1].sigmoid().cpu()
        mask_tensor = preds[0].squeeze(0)
        mask_image = to_pil(mask_tensor)
        mask_image = mask_image.resize(orig_size, Image.LANCZOS)

        # Create result image: add alpha channel from mask to original image
        output_image = original_image.copy()
        output_image.putalpha(mask_image)

        # If target_size is provided (user provided size parameter), resize output image
        if target_size is not None:
            output_image = output_image.resize(target_size, Image.LANCZOS)

        # Handle output format
        if out_format == "jpg":
            final_img = output_image.convert("RGB")
            out_ext = "jpg"
            mimetype = "image/jpeg"
            buf = io.BytesIO()
            final_img.save(buf, format="JPEG")
            buf.seek(0)
            return send_file(buf, mimetype=mimetype, as_attachment=False, download_name=f"output.{out_ext}")
        elif out_format == "zip":
            return jsonify({"error": "ZIP format not implemented in this demo"}), 400
        else:
            final_img = output_image
            out_ext = "png"
            mimetype = "image/png"
            buf = io.BytesIO()
            final_img.save(buf, format="PNG")
            buf.seek(0)
            return send_file(buf, mimetype=mimetype, as_attachment=False, download_name=f"output.{out_ext}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500