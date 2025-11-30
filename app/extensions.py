# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# ❗這裡只建立物件，不要傳 app 進來
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
