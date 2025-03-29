# config.py: Contains common configurations for the project

import torch

# Configure device for running the model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if DEVICE.type == "cuda":
    print("GPU detected:", torch.cuda.get_device_name(0))
else:
    print("No GPU detected, using CPU.")

# Model name from Hugging Face
MODEL_NAME = "ZhengPeng7/BiRefNet"

# Input size for model (resize image to 1024x1024 before feeding to model)
MODEL_INPUT_SIZE = (1024, 1024)