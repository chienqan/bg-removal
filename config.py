# config.py: Chứa các cấu hình chung cho dự án

import torch

# Cấu hình thiết bị chạy model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if DEVICE.type == "cuda":
    print("GPU detected:", torch.cuda.get_device_name(0))
else:
    print("No GPU detected, using CPU.")

# Model name từ Hugging Face
MODEL_NAME = "ZhengPeng7/BiRefNet"

# Kích thước đầu vào cho model (resize ảnh thành 1024x1024 trước khi đưa vào model)
MODEL_INPUT_SIZE = (1024, 1024)