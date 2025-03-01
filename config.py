# config.py: Chứa các cấu hình chung cho dự án

import torch

# Cấu hình thiết bị chạy model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model name từ Hugging Face
MODEL_NAME = "ZhengPeng7/BiRefNet"

# Kích thước đầu vào cho model (resize ảnh thành 1024x1024 trước khi đưa vào model)
MODEL_INPUT_SIZE = (1024, 1024)

# Các tham số mapping cho kích thước output (đơn giản minh họa)
SIZE_MAP = {
    "preview": (625, 400),
    "small": (625, 400),
    "regular": (625, 400),
    "medium": (1280, 720),
    "hd": (1920, 1080)
}