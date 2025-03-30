# utils/image_utils.py: Image processing utilities, reading images from various sources, base64 conversion, etc.
import base64
import io
import requests
from PIL import Image

def get_input_image(req):
    """
    Get input image from request.

    Supported form-data fields:
    - "image_file": Direct image file upload
    - "image_file_b64": Base64 encoded image
    - "image_url": URL to an image

    Priority: image_file > image_file_b64 > image_url
    """
    sources = {}
    image = None

    # Check file upload via "image_file"
    if "image_file" in req.files:
        try:
            sources["image_file"] = Image.open(req.files["image_file"].stream).convert("RGB")
        except Exception as e:
            raise ValueError(f"Error reading image_file: {str(e)}")
            
    # Check "image_file_b64" field in form data
    image_file_b64 = req.form.get("image_file_b64")
    if image_file_b64:
        try:
            decoded = base64.b64decode(image_file_b64)
            sources["image_file_b64"] = Image.open(io.BytesIO(decoded)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Error reading image_file_b64: {str(e)}")
            
    # Check "image_url" field in form data
    image_url = req.form.get("image_url")
    if image_url:
        try:
            # Add a proper User-Agent header to comply with website policies
            headers = {
                "User-Agent": "BgRemoverAPI/1.0 (github.com/deltora-ai/bg-removal; hello@deltora.ai)"
            }
            resp = requests.get(image_url, headers=headers)
            resp.raise_for_status()
            sources["image_url"] = Image.open(io.BytesIO(resp.content)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Error reading image_url: {str(e)}")

    if not sources:
        raise ValueError("No image source provided. Please use form-data with one of: image_file, image_file_b64, or image_url")

    # Priority: image_file > image_file_b64 > image_url
    if "image_file" in sources:
        image = sources["image_file"]
    elif "image_file_b64" in sources:
        image = sources["image_file_b64"]
    elif "image_url" in sources:
        image = sources["image_url"]

    if image is None:
        raise ValueError("No valid image source found.")

    return image