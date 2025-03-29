# routes/__init__.py: Register blueprints in the routes directory

from flask import Blueprint
from routes.remove_bg import remove_bg_bp
from routes.ping import ping_bp

def register_routes(app):
    app.register_blueprint(remove_bg_bp)
    app.register_blueprint(ping_bp)