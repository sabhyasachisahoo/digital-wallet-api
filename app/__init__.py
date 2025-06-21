from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wallet.db'
    db.init_app(app)

    # Register route blueprints
    from .routes.user_routes import user_bp
    from .routes.product_routes import product_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)

    with app.app_context():
        db.create_all()

    return app
