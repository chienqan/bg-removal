# BG-Remover API

BG-Remover is a Flask-based API for background removal using the BiRefNet model from Hugging Face via the Transformers library. The API accepts image inputs in multiple forms and allows customization of output resolution and format.

## Features

- **Input Options:**
  - `image_file`: Binary file upload (multipart/form-data)
  - `image_file_b64`: Base64-encoded image string
  - `image_url`: URL to an image

- **Output Parameters:**
  - `size`: Maximum output image resolution.
    - **Options:**
      - `"preview"` (default): 0.25 megapixels (e.g., 625×400 pixels)
      - `"medium"`: Up to 1.5 megapixels
      - `"hd"`: Up to 4 megapixels
      - `"full"` / `"4k"`: Original image resolution (up to 25 megapixels for ZIP/JPG or 10 megapixels for PNG)
      - `"50MP"`: Up to 50 megapixels (for specific cases)
      - `"auto"`: Highest available resolution based on image size and available credits
  - `format`: Result image format.
    - **Options:**
      - `"auto"` (default): PNG if transparent regions exist, otherwise JPG
      - `"png"`: PNG with alpha transparency
      - `"jpg"`: JPG without transparency
      - `"zip"`: ZIP archive containing both the color image and alpha matte (not implemented in the demo)

## Project Structure

```commandline
bg-remover/
├── app.py
├── config.py
├── requirements.txt
├── model/
│ ├── init.py
│ └── birefnet_model.py
├── routes/
│ ├── init.py
│ └── remove_bg.py
└── utils/
│ ├── init.py
│ ├── image_utils.py
│ └── param_utils.py
├── .gitgnore
└── README.MD
```

- **app.py:** Entry point for the Flask application.
- **config.py:** Contains configuration variables such as device settings, model name, and output size mappings.
- **requirements.txt:** Lists all Python package dependencies.
- **model/birefnet_model.py:** Loads the BiRefNet model via the Transformers library.
- **routes/remove_bg.py:** Defines the `/remove-bg` endpoint for processing background removal.
- **utils/image_utils.py:** Provides helper functions to load and process images from different sources (file upload, base64, URL).
- **utils/param_utils.py:** Contains helper functions to parse and map the `size` and `format` parameters.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/bg-remover.git
cd bg-remover
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

## Testing the API with cURL
Below are some example cURL commands to test the API with different input parameters.

1. ** Test with image_file (multipart/form-data)**

```bash
curl -X POST http://localhost:5000/remove-bg \
  -F "image_file=@/path/to/your/test_image.jpg" \
  -F "size=medium" \
  -F "format=png" \
  -o output_image_file.png
```

2. **Test with image_file_b64 (JSON payload)**

First, encode your image to Base64:
```bash
base64 /path/to/your/test_image.jpg > image.txt
```
Then, use the Base64 string from image.txt in the JSON payload:
```bash
curl -X POST http://localhost:5000/remove-bg \
  -H "Content-Type: application/json" \
  -d '{"image_file_b64": "YOUR_BASE64_ENCODED_STRING_HERE", "size": "hd", "format": "jpg"}' \
  -o output_image_file_b64.jpg
```

3. **Test with image_url (JSON payload)**
```bash
curl -X POST http://localhost:5000/remove-bg \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/test_image.jpg", "size": "preview", "format": "auto"}' \
  -o output_image_url.png
```

## Notes

- **Image Source:** Only one image source is allowed per request. If multiple sources (e.g., `image_file` and `image_url`) are provided, the API will return an error.
- **ZIP Format:** The `"zip"` format option is not implemented in this demo.
- **High-Resolution Processing:** For processing at resolutions like `"full"` or `"50MP"`, ensure your server has sufficient resources.
- **Model:** This API uses the BiRefNet model loaded via the Transformers library with `trust_remote_code=True`. Adjust the model or parameters as needed.

## License

This project is licensed under the MIT License.