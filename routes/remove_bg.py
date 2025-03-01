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
        # Lấy ảnh đầu vào từ request
        original_image = get_input_image(request)
        orig_size = original_image.size

        # Lấy các tham số "size" và "format"
        # Nếu không có, thì không xử lý resize và định dạng mặc định là png.
        if request.content_type.startswith("multipart/form-data"):
            size_param = request.form.get("size")  # Không có default
            fmt_param = request.form.get("format")   # Không có default
        elif request.is_json:
            json_data = request.get_json()
            size_param = json_data.get("size")
            fmt_param = json_data.get("format")
        else:
            size_param = None
            fmt_param = None

        # Tính kích thước mục tiêu dựa trên ảnh gốc và tham số size.
        target_size = compute_target_size(orig_size, size_param) if size_param else None
        # Định dạng output: nếu không có thì mặc định "png"
        out_format = get_output_format(fmt_param) if fmt_param else "png"

        # Chuyển đổi ảnh cho model: resize thành MODEL_INPUT_SIZE, chuyển thành tensor và chuẩn hóa
        transform_image = transforms.Compose([
            transforms.Resize(MODEL_INPUT_SIZE),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225])
        ])
        input_tensor = transform_image(original_image).unsqueeze(0).to(DEVICE)
        if DEVICE.type == "cuda":
            input_tensor = input_tensor.half()

        # Gọi model, lấy output cuối cùng và áp dụng sigmoid để có mask từ 0 đến 1
        with torch.no_grad():
            preds = birefnet_model(input_tensor)[-1].sigmoid().cpu()
        mask_tensor = preds[0].squeeze(0)
        mask_image = to_pil(mask_tensor)
        mask_image = mask_image.resize(orig_size, Image.LANCZOS)

        # Tạo ảnh kết quả: thêm kênh alpha từ mask vào ảnh gốc
        output_image = original_image.copy()
        output_image.putalpha(mask_image)

        # Nếu có target_size (user cung cấp tham số size) thì resize ảnh đầu ra
        if target_size is not None:
            output_image = output_image.resize(target_size, Image.LANCZOS)

        # Xử lý định dạng output
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