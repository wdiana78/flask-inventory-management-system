from flask import Flask
from app.routes.inventory_routes import inventory_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(inventory_bp)

    @app.route("/")
    def home():
        return {"message": "Inventory Management API"}

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    return app
