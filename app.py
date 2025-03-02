# app.py: File entrypoint của ứng dụng Flask
import warnings
warnings.filterwarnings('ignore')

from flask import Flask
from routes import register_routes

app = Flask(__name__)

# Register routes (blueprint)
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
