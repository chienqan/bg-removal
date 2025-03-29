# model/birefnet_model.py: Load BiRefNet model via transformers

from transformers import AutoModelForImageSegmentation
from config import MODEL_NAME, DEVICE
import torch

def load_birefnet_model():
    model = AutoModelForImageSegmentation.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model.to(DEVICE)
    model.eval()
    if DEVICE.type == "cuda":
        model.half()
    return model

# Initialize model once and use it throughout the project
birefnet_model = load_birefnet_model()