# app/__init__.py

from flask import Flask, jsonify
from config import Config
from .extensions import db, bcrypt, jwt


def create_app():
    app = Flask(__name__)

    # === 基本設定 ===
    app.config.from_object(Config)

    # 如果 Config 裡已經有設定可以不用，但這樣寫可以當預設值
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("JWT_SECRET_KEY", "super-secret-key")

    # === 初始化 extensions（每個只呼叫一次）===
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # === import models & blueprints（放在 init_app 之後，避免循環引用）===
    from . import models  # 確保資料表的 model 都載入
    from .routes.auth_routes import auth_bp
    from .routes.project_routes import project_bp
    from .routes.content_routes import content_bp
    from .routes.version_routes import version_bp
    from .routes.tag_routes import tag_bp
    from .routes.search_routes import search_bp

    # === 建立所有資料表 ===
    with app.app_context():
        db.create_all()

    # === 註冊藍圖 ===
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(content_bp, url_prefix="/api/contents")
    app.register_blueprint(version_bp, url_prefix="/api/versions")
    app.register_blueprint(tag_bp, url_prefix="/api/tags")
    app.register_blueprint(search_bp, url_prefix="/api/search")

    # ✅ Health Check（不碰資料庫）
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    return app
