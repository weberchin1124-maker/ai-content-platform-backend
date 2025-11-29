from flask import Flask
from config import Config
from .extensions import db, bcrypt, jwt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化擴充
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # 避免循環匯入，在這裡再 import 路由
    from .routes.auth_routes import auth_bp
    from .routes.project_routes import project_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(project_bp, url_prefix="/api/projects")

    return app

