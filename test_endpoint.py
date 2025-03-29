import requests
import os
from PIL import Image
import base64
from models.bg_remover import remove

def test_with_file(image_path, output_path):
    """
    Test the endpoint with a local image file
    """
    url = "http://localhost:5000/remove-bg"
    
    # Open and prepare the image file
    with open(image_path, 'rb') as img_file:
        files = {
            'image_file': ('image.jpg', img_file, 'image/jpeg')
        }
        
        print(f"Testing with file: {image_path}")
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            # Save the response image
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Success! Output saved to: {output_path}")
        else:
            print(f"Error: {response.status_code}")
            print(response.json())

def test_with_url(image_url, output_path):
    """
    Test the endpoint with an image URL
    """
    url = "http://localhost:5000/remove-bg"
    
    data = {
        'image_url': image_url
    }
    
    print(f"Testing with URL: {image_url}")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        # Save the response image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Success! Output saved to: {output_path}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

def test_with_base64(image_path, output_path):
    """
    Test the endpoint with a base64 encoded image
    """
    url = "http://localhost:5000/remove-bg"
    
    # Read and encode the image
    with open(image_path, 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    data = {
        'image_file_b64': img_base64
    }
    
    print(f"Testing with base64 encoded image: {image_path}")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        # Save the response image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Success! Output saved to: {output_path}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("test_outputs", exist_ok=True)
    
    # Test with a local file
    test_with_file(
        "test_images/test1.jpg",  # Replace with your image path
        "test_outputs/output_file.png"
    )
    
    # Test with a URL
    test_with_url(
        "https://example.com/test_image.jpg",  # Replace with your image URL
        "test_outputs/output_url.png"
    )
    
    # Test with base64
    test_with_base64(
        "test_images/test2.jpg",  # Replace with your image path
        "test_outputs/output_base64.png"
    ) 