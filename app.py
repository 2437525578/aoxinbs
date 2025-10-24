import logging
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from routes.user_routes import user_bp
from database import db
from config import Config
from models import Chemical, User # Import all models

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    mail.init_app(app)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.logger.setLevel(logging.INFO)

    from routes.chemical_routes import chemical_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(chemical_bp, url_prefix='/api/chemical')

    @app.route('/')
    def index():
        return 'Hello Flask! 实验室危化品管理系统后端运行成功'

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
