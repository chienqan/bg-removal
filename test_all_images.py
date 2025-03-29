import os
from PIL import Image
from datetime import datetime
from models.bg_remover import remove

def test_with_file(image_path, output_path):
    """
    Test background removal with a local image file
    """
    try:
        # Process the image
        print(f"Testing with file: {image_path}")
        result = remove(image_path)
        
        # Save the result
        result.save(output_path, 'PNG')
        print(f"Success! Output saved to: {output_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

def test_all_images():
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"test_outputs_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files from test_images directory
    image_files = [f for f in os.listdir("test_images") 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg')) 
                  and not f.startswith('.')]
    
    print(f"Found {len(image_files)} images to test")
    
    # Test each image
    for image_file in image_files:
        image_path = os.path.join("test_images", image_file)
        base_name = os.path.splitext(image_file)[0]
        
        print(f"\nProcessing: {image_file}")
        
        output_name = f"{base_name}_output.png"
        output_path = os.path.join(output_dir, output_name)
        
        test_with_file(
            image_path,
            output_path
        )

if __name__ == "__main__":
    print("Starting background removal tests...")
    test_all_images()
    print("\nAll tests completed!") 