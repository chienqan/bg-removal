# utils/image_utils.py: Các hàm xử lý ảnh, đọc ảnh từ nhiều nguồn, chuyển đổi base64,...
import base64
import io
import requests
from PIL import Image

def get_input_image(req):
    """
    Lấy ảnh đầu vào từ request.

    - Nếu Content-Type là multipart/form-data:
        Hỗ trợ các trường: "image_file", "image_file_b64" và "image_url".
        Ưu tiên: image_file > image_file_b64 > image_url.
    - Nếu Content-Type là application/json:
        Chỉ hỗ trợ các trường: "image_file_b64" và "image_url",
        Ưu tiên: image_file_b64 > image_url.
    """
    sources = {}
    image = None

    if req.content_type.startswith("multipart/form-data"):
        # Kiểm tra file upload qua "image_file"
        if "image_file" in req.files:
            try:
                sources["image_file"] = Image.open(req.files["image_file"].stream).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error reading image_file: {str(e)}")
        # Kiểm tra trường "image_file_b64" trong form data
        image_file_b64 = req.form.get("image_file_b64")
        if image_file_b64:
            try:
                decoded = base64.b64decode(image_file_b64)
                sources["image_file_b64"] = Image.open(io.BytesIO(decoded)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error reading image_file_b64: {str(e)}")
        # Kiểm tra trường "image_url" trong form data
        image_url = req.form.get("image_url")
        if image_url:
            try:
                resp = requests.get(image_url)
                resp.raise_for_status()
                sources["image_url"] = Image.open(io.BytesIO(resp.content)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error reading image_url: {str(e)}")
    elif req.is_json:
        json_data = req.get_json()
        if "image_file_b64" in json_data:
            try:
                decoded = base64.b64decode(json_data["image_file_b64"])
                sources["image_file_b64"] = Image.open(io.BytesIO(decoded)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error reading image_file_b64: {str(e)}")
        if "image_url" in json_data:
            try:
                resp = requests.get(json_data["image_url"])
                resp.raise_for_status()
                sources["image_url"] = Image.open(io.BytesIO(resp.content)).convert("RGB")
            except Exception as e:
                raise ValueError(f"Error reading image_url: {str(e)}")
    else:
        raise ValueError("Unsupported content type. Use multipart/form-data or application/json.")

    if not sources:
        raise ValueError("No image source provided.")

    # Đối với multipart/form-data, ưu tiên: image_file > image_file_b64 > image_url.
    if req.content_type.startswith("multipart/form-data"):
        if "image_file" in sources:
            image = sources["image_file"]
        elif "image_file_b64" in sources:
            image = sources["image_file_b64"]
        elif "image_url" in sources:
            image = sources["image_url"]
    else:
        # Với JSON, chỉ có image_file_b64 và image_url
        if "image_file_b64" in sources:
            image = sources["image_file_b64"]
        elif "image_url" in sources:
            image = sources["image_url"]

    if image is None:
        raise ValueError("No valid image source found.")

    return image