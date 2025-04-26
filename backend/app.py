from flask import Flask
from config import DevelopmentConfig
from dotenv import load_dotenv

load_dotenv()

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from routes.diff import diff_bp
    app.register_blueprint(diff_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

