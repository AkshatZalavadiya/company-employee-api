from flask import Flask
from .models import db
from .routes import api_bp
import os


def create_app():
    """
    Application factory function. Creates and configures the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        
    return app
