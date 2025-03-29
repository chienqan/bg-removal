import torch
from PIL import Image
from torchvision import transforms
from models.birefnet_model import birefnet_model
from config import DEVICE, MODEL_INPUT_SIZE

def remove(image):
    """
    Remove background from an image using the BiRefNet model
    
    Args:
        image: PIL Image or path to image file
        
    Returns:
        PIL Image with transparent background
    """
    # If image is a file path, open it
    if isinstance(image, str):
        image = Image.open(image).convert("RGB")
    
    # Make sure image is in RGB mode
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Save original size for later
    orig_size = image.size
    
    # Transform image for the model
    transform_image = transforms.Compose([
        transforms.Resize(MODEL_INPUT_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                            [0.229, 0.224, 0.225])
    ])
    
    # Prepare input tensor
    input_tensor = transform_image(image).unsqueeze(0).to(DEVICE)
    if DEVICE.type == "cuda":
        input_tensor = input_tensor.half()
    
    # Run model
    to_pil = transforms.ToPILImage()
    with torch.no_grad():
        preds = birefnet_model(input_tensor)[-1].sigmoid().cpu()
    mask_tensor = preds[0].squeeze(0)
    mask_image = to_pil(mask_tensor)
    mask_image = mask_image.resize(orig_size, Image.LANCZOS)
    
    # Create result image with alpha channel
    output_image = image.copy()
    output_image.putalpha(mask_image)
    
    return output_image 