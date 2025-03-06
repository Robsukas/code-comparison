from flask import Flask
from config import DevelopmentConfig
from flask_cors import CORS

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    from routes.diff import diff_bp
    app.register_blueprint(diff_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000)
