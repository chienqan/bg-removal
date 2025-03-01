# routes/__init__.py: Đăng ký các blueprint trong thư mục routes

from flask import Blueprint
from routes.remove_bg import remove_bg_bp

def register_routes(app):
    app.register_blueprint(remove_bg_bp)