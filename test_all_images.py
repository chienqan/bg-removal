import os
import sys
import argparse
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from models.bg_remover import remove, is_sky_region

def compare_images(original_path, result_path, comparison_path, title=None):
    """
    Create a comparison image showing original and result side by side
    """
    # Open images
    original = Image.open(original_path)
    result = Image.open(result_path)
    
    # Create a white background to place both images
    # First resize both images to have the same height (while preserving aspect ratio)
    max_height = 500  # Limit max height for display purposes
    
    # Calculate new dimensions while preserving aspect ratio
    orig_width, orig_height = original.size
    result_width, result_height = result.size
    
    # Scale both images to same height
    new_height = min(orig_height, result_height, max_height)
    orig_scale = new_height / orig_height
    result_scale = new_height / result_height
    
    new_orig_width = int(orig_width * orig_scale)
    new_result_width = int(result_width * result_scale)
    
    # Resize images
    original_resized = original.resize((new_orig_width, new_height), Image.LANCZOS)
    result_resized = result.resize((new_result_width, new_height), Image.LANCZOS)
    
    # Create a new image with enough width for both images and some padding
    padding = 20
    comparison = Image.new('RGB', 
                         (new_orig_width + new_result_width + 3*padding, 
                          new_height + 2*padding + 30),  # Extra height for text
                         (255, 255, 255))
    
    # Paste the images
    comparison.paste(original_resized, (padding, padding))
    comparison.paste(result_resized, (new_orig_width + 2*padding, padding))
    
    # Add text labels
    try:
        draw = ImageDraw.Draw(comparison)
        # Try to get a font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial", 20)
        except:
            font = ImageFont.load_default()
        
        # Add labels
        draw.text((padding, new_height + padding), "Original", fill=(0, 0, 0), font=font)
        draw.text((new_orig_width + 2*padding, new_height + padding), "Background Removed", fill=(0, 0, 0), font=font)
        
        # Add title if provided
        if title:
            draw.text((padding, 5), title, fill=(0, 0, 0), font=font)
            
    except Exception as e:
        print(f"Warning: Could not add text to comparison image: {str(e)}")
    
    # Save comparison image
    comparison.save(comparison_path)
    print(f"Saved comparison to: {comparison_path}")
    
    return comparison

def create_debug_visualization(image_path, base_name, debug_dir):
    """
    Create debug visualizations of the mask generation process
    
    Args:
        image_path: Path to the input image
        base_name: Base name for output files
        debug_dir: Directory to save debug images
    """
    try:
        # Load the image
        image = Image.open(image_path).convert('RGB')
        img_np = np.array(image)
        h, w, _ = img_np.shape
        
        # Create an all white mask to start (255 = keep, 0 = remove)
        mask_np = np.ones((h, w), dtype=np.uint8) * 255
        
        # Function to detect sky pixels
        def detect_sky_pixels(img, threshold=0.8):
            sky_mask = np.zeros((h, w), dtype=np.uint8)
            for y in range(h):
                for x in range(w):
                    r, g, b = img[y, x]
                    # Check for blue sky
                    is_blue_sky = b > r and b > g and b > 100
                    # Check for white/gray sky
                    brightness = (int(r) + int(g) + int(b)) / 3.0
                    is_bright = (brightness > 200 and 
                                abs(int(r) - int(g)) < 20 and 
                                abs(int(r) - int(b)) < 20 and 
                                abs(int(g) - int(b)) < 20)
                    if is_blue_sky or is_bright:
                        sky_mask[y, x] = 255
            return sky_mask
        
        # Generate sky detection mask
        print("Generating sky detection mask...")
        sky_mask = detect_sky_pixels(img_np)
        
        # Apply more aggressive detection to upper quarter
        sky_mask_top = sky_mask.copy()
        upper_region = np.zeros((h//4, w), dtype=np.uint8)
        for y in range(h//4):
            for x in range(w):
                # Check surrounding pixels
                count = 0
                for dy in [-2, -1, 0, 1, 2]:
                    for dx in [-2, -1, 0, 1, 2]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h//4 and 0 <= nx < w and sky_mask[ny, nx] > 0:
                            count += 1
                
                # If surrounded by many sky pixels, likely sky
                if count > 15:
                    upper_region[y, x] = 255
        
        # Inverted masks (for display - white is background, black is foreground)
        # Note: in implementation, 255 = keep, 0 = remove, but for display we invert
        sky_mask_display = 255 - sky_mask  
        upper_region_display = np.zeros_like(sky_mask_display)
        upper_region_display[:h//4, :] = 255 - upper_region
        
        # Create masked images
        sky_only = img_np.copy()
        sky_only[sky_mask == 0] = [255, 255, 255]  # Make non-sky white
        
        upper_only = img_np.copy()
        temp_mask = np.ones_like(sky_mask) * 255
        temp_mask[:h//4, :] = upper_region
        upper_only[temp_mask == 0] = [255, 255, 255]  # Make non-sky white
        
        # Combined mask for actual use (255 = keep, 0 = remove)
        combined_mask = np.maximum(sky_mask, np.zeros_like(sky_mask))
        combined_mask[:h//4, :] = np.maximum(upper_region, np.zeros_like(upper_region))
        
        # For display we invert (white = background)
        combined_mask_display = 255 - combined_mask
        
        # Create final visualization with alpha
        final_result = img_np.copy()
        final_result[combined_mask == 0] = [255, 255, 255]  # Make background white
        
        # Save all masks and visualizations
        Image.fromarray(sky_mask_display).save(os.path.join(debug_dir, f"{base_name}_sky_mask.png"))
        Image.fromarray(upper_region_display).save(os.path.join(debug_dir, f"{base_name}_upper_mask.png"))
        Image.fromarray(combined_mask_display).save(os.path.join(debug_dir, f"{base_name}_combined_mask.png"))
        Image.fromarray(sky_only).save(os.path.join(debug_dir, f"{base_name}_sky_only.png"))
        Image.fromarray(upper_only).save(os.path.join(debug_dir, f"{base_name}_upper_only.png"))
        Image.fromarray(final_result).save(os.path.join(debug_dir, f"{base_name}_masked.png"))
        
        # Create a complete debug grid visualization
        scale_factor = 0.25  # Scale down for easier viewing
        thumbnail_size = (int(w * scale_factor), int(h * scale_factor))
        
        # Create thumbnails
        original_thumb = Image.fromarray(img_np).resize(thumbnail_size, Image.LANCZOS)
        sky_mask_thumb = Image.fromarray(sky_mask_display).resize(thumbnail_size, Image.LANCZOS)
        upper_mask_thumb = Image.fromarray(upper_region_display).resize(thumbnail_size, Image.LANCZOS)
        combined_mask_thumb = Image.fromarray(combined_mask_display).resize(thumbnail_size, Image.LANCZOS)
        sky_only_thumb = Image.fromarray(sky_only).resize(thumbnail_size, Image.LANCZOS)
        upper_only_thumb = Image.fromarray(upper_only).resize(thumbnail_size, Image.LANCZOS)
        final_thumb = Image.fromarray(final_result).resize(thumbnail_size, Image.LANCZOS)
        
        # Get BiRefNet results for comparison
        try:
            # Process with BiRefNet
            from models.bg_remover import remove
            birefnet_result = remove(image_path)
            birefnet_result_np = np.array(birefnet_result.convert('RGBA'))
            birefnet_thumb = Image.fromarray(birefnet_result_np).resize(thumbnail_size, Image.LANCZOS)
        except Exception as e:
            print(f"Warning: Could not get BiRefNet results: {str(e)}")
            birefnet_thumb = Image.new('RGBA', thumbnail_size, (255, 0, 0, 128))
        
        # Create grid layout
        padding = 10
        grid_width = thumbnail_size[0] * 4 + padding * 5
        grid_height = thumbnail_size[1] * 2 + padding * 4 + 60  # Extra for title and labels
        
        grid = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        
        # Add thumbnails to grid
        # Row 1
        grid.paste(original_thumb, (padding, padding + 40))
        grid.paste(sky_mask_thumb, (padding * 2 + thumbnail_size[0], padding + 40))
        grid.paste(upper_mask_thumb, (padding * 3 + thumbnail_size[0] * 2, padding + 40))
        grid.paste(combined_mask_thumb, (padding * 4 + thumbnail_size[0] * 3, padding + 40))
        
        # Row 2
        grid.paste(sky_only_thumb, (padding, padding * 2 + thumbnail_size[1] + 40))
        grid.paste(upper_only_thumb, (padding * 2 + thumbnail_size[0], padding * 2 + thumbnail_size[1] + 40))
        grid.paste(final_thumb, (padding * 3 + thumbnail_size[0] * 2, padding * 2 + thumbnail_size[1] + 40))
        grid.paste(birefnet_thumb.convert('RGB'), (padding * 4 + thumbnail_size[0] * 3, padding * 2 + thumbnail_size[1] + 40))
        
        # Add text labels
        draw = ImageDraw.Draw(grid)
        try:
            font = ImageFont.truetype("Arial", 16)
            small_font = ImageFont.truetype("Arial", 12)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Title
        draw.text((padding, 10), f"Sky Detection Debug: {os.path.basename(image_path)}", 
                fill=(0, 0, 0), font=font)
        
        # Row 1 labels
        label_y = padding + 20
        draw.text((padding, label_y), "Original Image", fill=(0, 0, 0), font=small_font)
        draw.text((padding * 2 + thumbnail_size[0], label_y), "Sky Mask", fill=(0, 0, 0), font=small_font)
        draw.text((padding * 3 + thumbnail_size[0] * 2, label_y), "Upper Region Mask", fill=(0, 0, 0), font=small_font)
        draw.text((padding * 4 + thumbnail_size[0] * 3, label_y), "Combined Mask", fill=(0, 0, 0), font=small_font)
        
        # Row 2 labels
        label_y = padding + thumbnail_size[1] + 40 + 5
        draw.text((padding, label_y), "Sky Detection Only", fill=(0, 0, 0), font=small_font)
        draw.text((padding * 2 + thumbnail_size[0], label_y), "Upper Region Only", fill=(0, 0, 0), font=small_font)
        draw.text((padding * 3 + thumbnail_size[0] * 2, label_y), "Final Result", fill=(0, 0, 0), font=small_font)
        draw.text((padding * 4 + thumbnail_size[0] * 3, label_y), "BiRefNet Result", fill=(0, 0, 0), font=small_font)
        
        # Save the debug grid
        grid.save(os.path.join(debug_dir, f"{base_name}_debug_grid.png"))
        
        print(f"Saved comprehensive debug visualizations to {debug_dir}")
        
        return True
    except Exception as e:
        print(f"Error creating debug visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_file(image_path, output_path, comparison_path, args):
    """
    Test background removal with a local image file
    
    Args:
        image_path: Path to input image
        output_path: Path to save output image
        comparison_path: Path to save comparison image
        args: Command line arguments
    
    Returns:
        Tuple containing (success flag, processing time)
    """
    try:
        # Create debug visualization if requested
        if args.debug_mode:
            debug_dir = os.path.join(os.path.dirname(output_path), "debug")
            os.makedirs(debug_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            create_debug_visualization(image_path, base_name, debug_dir)
        
        # Start timing
        start_time = time.time()
        
        # Process the image
        print(f"Testing with file: {image_path}")
        result = remove(image_path)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Save the result
        result.save(output_path, 'PNG')
        print(f"Success! Output saved to: {output_path}")
        print(f"Processing time: {process_time:.2f} seconds")
        
        # Create comparison image if requested
        if args.create_comparisons:
            compare_images(image_path, output_path, comparison_path)
        
        return True, process_time
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return False, 0

def test_all_images(args):
    """
    Test background removal on all images in test_images directory
    
    Args:
        args: Command line arguments
    """
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"test_outputs_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create comparisons directory if needed
    comparisons_dir = os.path.join(output_dir, "comparisons")
    if args.create_comparisons:
        os.makedirs(comparisons_dir, exist_ok=True)
    
    # Get all image files from test_images directory
    input_dir = args.input_dir if args.input_dir else "test_images"
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return False
    
    image_files = [f for f in os.listdir(input_dir) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg')) 
                  and not f.startswith('.')]
    
    # Sort for consistency
    image_files.sort()
    
    if len(image_files) == 0:
        print(f"Error: No images found in '{input_dir}'")
        return False
    
    print(f"Found {len(image_files)} images to test")
    
    # Initialize counters
    success_count = 0
    total_time = 0
    
    # Test each image
    for i, image_file in enumerate(image_files):
        # Skip non-target images if specific targets are provided
        if args.target_files and image_file not in args.target_files:
            continue
            
        image_path = os.path.join(input_dir, image_file)
        base_name = os.path.splitext(image_file)[0]
        
        print(f"\n[{i+1}/{len(image_files)}] Processing: {image_file}")
        
        output_name = f"{base_name}_output.png"
        output_path = os.path.join(output_dir, output_name)
        comparison_path = os.path.join(comparisons_dir, f"{base_name}_comparison.jpg")
        
        # Test the image
        success, process_time = test_with_file(
            image_path,
            output_path,
            comparison_path,
            args
        )
        
        if success:
            success_count += 1
            total_time += process_time
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total images: {len(image_files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(image_files) - success_count}")
    if success_count > 0:
        print(f"Average processing time: {total_time/success_count:.2f} seconds")
    print(f"Output directory: {output_dir}")
    print("="*50)
    
    return success_count == len(image_files)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test background removal on images")
    
    parser.add_argument("--input-dir", type=str, default="test_images",
                        help="Directory containing test images (default: test_images)")
    parser.add_argument("--create-comparisons", action="store_true",
                        help="Create side-by-side comparison images")
    parser.add_argument("--verbose", action="store_true",
                        help="Print more detailed output")
    parser.add_argument("--debug-mode", action="store_true",
                        help="Create debug visualizations of the mask generation process")
    parser.add_argument("--target-files", nargs="+", type=str,
                        help="Specific files to target for testing")
    
    return parser.parse_args()

if __name__ == "__main__":
    print("Starting background removal tests...")
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Run tests
    success = test_all_images(args)
    
    # Exit with appropriate code
    if success:
        print("\nAll tests completed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the logs above.")
        sys.exit(1) 