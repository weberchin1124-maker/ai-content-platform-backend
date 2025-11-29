##下面欄位是「簡化版示意」，你要依照你自己的 DDL 把欄位名稱、型態改成一樣。
##重點是：__table_args__ = {'schema': 'g9'} 要加進去，才會指到你們的 schema。


from datetime import datetime
from .extensions import db
from config import Config

schema_name = Config.PG_SCHEMA  # "g9"

class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"schema": schema_name}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = "project"
    __table_args__ = {"schema": schema_name}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey(f"{schema_name}.user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", backref="owned_projects")

class ProjectMember(db.Model):
    __tablename__ = "project_member"
    __table_args__ = {"schema": schema_name}

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(f"{schema_name}.project.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(f"{schema_name}.user.id"), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # owner/editor/viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", backref="members")
    user = db.relationship("User", backref="project_memberships")
