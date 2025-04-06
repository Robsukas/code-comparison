from flask import Flask
from config import DevelopmentConfig
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    from routes.diff import diff_bp
    app.register_blueprint(diff_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000)

