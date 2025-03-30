# Background Removal API

BG-Removal is a Flask-based API for background removal using the BiRefNet model from Hugging Face via the Transformers library. The API accepts image inputs in multiple forms and returns PNG images with transparency.

## Features

- **Input Options (form-data only):**
  - `image_file`: Binary file upload
  - `image_file_b64`: Base64-encoded image string
  - `image_url`: URL to an image

- **Output:**
  - PNG image with transparency
  - Original dimensions preserved

## Project Structure

```commandline
bg-removal/
├── app.py
├── config.py
├── requirements.txt
├── test_endpoints.py
├── models/
│ ├── __init__.py
│ ├── bg_remover.py
│ └── birefnet_model.py
├── routes/
│ ├── __init__.py
│ ├── ping.py
│ └── remove_bg.py
└── utils/
  ├── __init__.py
  └── image_utils.py
```

- **app.py:** Entry point for the Flask application.
- **config.py:** Contains configuration variables such as device settings and model name.
- **requirements.txt:** Lists all Python package dependencies.
- **test_endpoints.py:** Test script to verify all input methods and endpoints.
- **models/birefnet_model.py:** Loads the BiRefNet model via the Transformers library.
- **models/bg_remover.py:** Core functionality for background removal.
- **routes/ping.py:** Defines health check and ping endpoints.
- **routes/remove_bg.py:** Defines the `/remove-bg` endpoint for processing background removal.
- **utils/image_utils.py:** Provides helper functions to load and process images from different sources (file upload, base64, URL).

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/bg-removal.git
cd bg-removal
```

2. **Create a virtual environment and activate it:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install required packages:**
```bash
pip install -r requirements.txt
```

## Running the API

To start the Flask server, run:
```bash
python app.py
```

By default, the server runs on port 5000. You can change this by setting the PORT environment variable:
```bash
PORT=5001 python app.py
```

## Testing the API

You can use the included test script to verify all endpoints:
```bash
python test_endpoints.py
```

Or with custom parameters:
```bash
python test_endpoints.py --host api.example.com --port 5001 --test-image my_image.jpg
```

## Testing the API with cURL
Below are example cURL commands to test the API with different input parameters.

1. **Test with image_file (multipart/form-data)**

```bash
curl -X POST http://localhost:5000/remove-bg \
  -F "image_file=@/path/to/your/test_image.jpg" \
  -o output_image_file.png
```

2. **Test with image_file_b64 (form-data)**

First, encode your image to Base64:
```bash
base64 /path/to/your/test_image.jpg > image.txt
```
Then, use the Base64 string from image.txt in the form-data:
```bash
curl -X POST http://localhost:5000/remove-bg \
  -F "image_file_b64=$(cat image.txt)" \
  -o output_image_file_b64.png
```

3. **Test with image_url (form-data)**
```bash
curl -X POST http://localhost:5000/remove-bg \
  -F "image_url=https://example.com/test_image.jpg" \
  -o output_image_url.png
```

## Notes

- **Image Source:** Only one image source is allowed per request. If multiple sources (e.g., `image_file` and `image_url`) are provided, the API will prioritize them in the following order: image_file > image_file_b64 > image_url.
- **Model:** This API uses the BiRefNet model loaded via the Transformers library with `trust_remote_code=True`.

## License

This project is licensed under the MIT License.