#!/usr/bin/env python
"""
Test script for the background removal API endpoints.
Tests all three input methods:
1. image_file - Direct file upload
2. image_url - URL to an image
3. image_file_b64 - Base64 encoded image

Also includes a batch processing test for all images in the test_images directory.

Usage:
    python test_endpoints.py [--host localhost] [--port 5000] [--batch]
"""

import argparse
import base64
import os
import sys
import time
import requests
from PIL import Image
import io
from datetime import datetime

def test_file_upload(host, port, test_image_path):
    """Test background removal with direct file upload"""
    print(f"\n[1/3] Testing direct file upload with {test_image_path}...")
    
    url = f"http://{host}:{port}/remove-bg"
    output_path = f"test_output_file.png"
    
    try:
        with open(test_image_path, "rb") as f:
            files = {"image_file": f}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            # Save the result
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Verify it's a valid image
            img = Image.open(output_path)
            print(f"✅ Success! Image size: {img.width}x{img.height}, Mode: {img.mode}")
            print(f"   Output saved to: {output_path}")
            return True
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_url_input(host, port, image_url):
    """Test background removal with image URL"""
    print(f"\n[2/3] Testing image URL with {image_url}...")
    
    url = f"http://{host}:{port}/remove-bg"
    output_path = f"test_output_url.png"
    
    try:
        data = {"image_url": image_url}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            # Save the result
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Verify it's a valid image
            img = Image.open(output_path)
            print(f"✅ Success! Image size: {img.width}x{img.height}, Mode: {img.mode}")
            print(f"   Output saved to: {output_path}")
            return True
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_base64_input(host, port, test_image_path):
    """Test background removal with base64 encoded image"""
    print(f"\n[3/3] Testing base64 encoded image with {test_image_path}...")
    
    url = f"http://{host}:{port}/remove-bg"
    output_path = f"test_output_base64.png"
    
    try:
        # Read and encode the image
        with open(test_image_path, "rb") as f:
            image_content = f.read()
        
        encoded_image = base64.b64encode(image_content).decode("utf-8")
        data = {"image_file_b64": encoded_image}
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            # Save the result
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Verify it's a valid image
            img = Image.open(output_path)
            print(f"✅ Success! Image size: {img.width}x{img.height}, Mode: {img.mode}")
            print(f"   Output saved to: {output_path}")
            return True
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_health_endpoint(host, port):
    """Test the health endpoint"""
    print(f"\n[+] Testing health endpoint...")
    
    url = f"http://{host}:{port}/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ Health endpoint successful: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing health endpoint: {str(e)}")
        return False

def test_ping_endpoint(host, port):
    """Test the ping endpoint"""
    print(f"\n[+] Testing ping endpoint...")
    
    url = f"http://{host}:{port}/ping"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ Ping endpoint successful: {response.json()}")
            return True
        else:
            print(f"❌ Ping endpoint failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing ping endpoint: {str(e)}")
        return False

def test_batch_processing(host, port):
    """Test batch processing of all images in test_images directory"""
    print("\n" + "=" * 40)
    print("BATCH PROCESSING TEST")
    print("=" * 40)
    
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"test_outputs_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Get all image files from test_images directory
    image_files = [f for f in os.listdir("test_images") 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg')) 
                  and not f.startswith('.')]
    
    print(f"Found {len(image_files)} images to test")
    
    # Process counter
    success_count = 0
    failure_count = 0
    
    # Test each image
    for image_file in image_files:
        image_path = os.path.join("test_images", image_file)
        base_name = os.path.splitext(image_file)[0]
        output_name = f"{base_name}_output.png"
        output_path = os.path.join(output_dir, output_name)
        
        print(f"\nProcessing: {image_file}")
        
        url = f"http://{host}:{port}/remove-bg"
        
        try:
            with open(image_path, "rb") as f:
                files = {"image_file": f}
                response = requests.post(url, files=files)
                
            if response.status_code == 200:
                # Save the result
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                # Verify it's a valid image
                img = Image.open(output_path)
                print(f"✅ Success! Image size: {img.width}x{img.height}, Mode: {img.mode}")
                print(f"   Output saved to: {output_path}")
                success_count += 1
            else:
                print(f"❌ Failed with status code: {response.status_code}")
                print(f"   Response: {response.text}")
                failure_count += 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            failure_count += 1
    
    print("\n" + "=" * 40)
    print(f"BATCH PROCESSING RESULTS: {success_count}/{len(image_files)} successful")
    print("=" * 40)
    
    return success_count == len(image_files)

def main():
    parser = argparse.ArgumentParser(description="Test the background removal API endpoints")
    parser.add_argument("--host", default="localhost", help="API host (default: localhost)")
    parser.add_argument("--port", default=5000, type=int, help="API port (default: 5000)")
    parser.add_argument("--test-image", default="test_images/adidas.jpeg", help="Path to test image (default: test_images/adidas.jpeg)")
    parser.add_argument("--test-url", default="https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg", 
                        help="URL to test image")
    parser.add_argument("--batch", action="store_true", help="Run batch processing test on all images in test_images directory")
    args = parser.parse_args()
    
    # Print test configuration
    print("=" * 40)
    print("BACKGROUND REMOVAL API ENDPOINT TESTS")
    print("=" * 40)
    print(f"API Host: {args.host}")
    print(f"API Port: {args.port}")
    print(f"Test Image: {args.test_image}")
    print(f"Test URL: {args.test_url}")
    print(f"Batch Processing: {'Enabled' if args.batch else 'Disabled'}")
    print("=" * 40)
    
    # Test health and ping endpoints first
    health_success = test_health_endpoint(args.host, args.port)
    ping_success = test_ping_endpoint(args.host, args.port)
    
    if not (health_success and ping_success):
        print("\n❌ Basic API endpoints failed. Please ensure the API server is running.")
        sys.exit(1)
    
    # Test all three background removal methods
    file_success = test_file_upload(args.host, args.port, args.test_image)
    url_success = test_url_input(args.host, args.port, args.test_url)
    base64_success = test_base64_input(args.host, args.port, args.test_image)
    
    # Run batch processing test if requested
    batch_success = True
    if args.batch:
        batch_success = test_batch_processing(args.host, args.port)
    
    # Print summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    print(f"Health Endpoint: {'✅ Passed' if health_success else '❌ Failed'}")
    print(f"Ping Endpoint: {'✅ Passed' if ping_success else '❌ Failed'}")
    print(f"File Upload: {'✅ Passed' if file_success else '❌ Failed'}")
    print(f"URL Input: {'✅ Passed' if url_success else '❌ Failed'}")
    print(f"Base64 Input: {'✅ Passed' if base64_success else '❌ Failed'}")
    if args.batch:
        print(f"Batch Processing: {'✅ Passed' if batch_success else '❌ Failed'}")
    print("=" * 40)
    
    if file_success and url_success and base64_success and batch_success:
        print("\n✅ All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 