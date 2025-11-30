
# app/models.py
from datetime import datetime
from .extensions import db


# ======================
# User
# ======================
class User(db.Model):
    __tablename__ = "user"  # 表名：user

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================
# Project
# ======================
class Project(db.Model):
    __tablename__ = "project"  # ✅ 改成單數：project （跟下面外鍵對應）

    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # ✅ 外鍵要指向 user.user_id（因為 User.__tablename__ = "user"）
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False,
    )

    # 方便透過 project.owner 拿到 User
    owner = db.relationship("User", backref=db.backref("projects", lazy=True))


# ======================
# ProjectMember
# ======================
class ProjectMember(db.Model):
    __tablename__ = "project_member"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.project_id"),  # ✅ 對應 Project.__tablename__ = "project"
        nullable=False,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False,
    )
    role = db.Column(db.String(20), nullable=False)  # owner/editor/viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", backref="members")
    user = db.relationship("User", backref="project_memberships")


# ======================
# Content
# ======================
class Content(db.Model):
    __tablename__ = "content"

    content_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey("project.project_id"),  # ✅ 一樣指向 project.project_id
        nullable=False,
    )
    creator_user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
    )
    # 指向「最新版本」那一筆 content_version
    latest_version_id = db.Column(
        db.Integer,
        db.ForeignKey("content_version.version_id"),
    )

    title = db.Column(db.String(255), nullable=False)
    primary_type = db.Column(db.String(30), nullable=False)  # text/image/...
    source_tool = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", backref="contents")
    creator = db.relationship(
        "User",
        backref="created_contents",
        foreign_keys=[creator_user_id],
    )

    # ✅ 一個 Content 有很多 Version（透過 content_version.content_id）
    versions = db.relationship(
        "ContentVersion",
        back_populates="content",
        foreign_keys="ContentVersion.content_id",
        cascade="all, delete-orphan",
    )

    # ✅ 這邊只透過 latest_version_id 連到單一版本
    latest_version = db.relationship(
        "ContentVersion",
        foreign_keys=[latest_version_id],
        uselist=False,
        post_update=True,
    )


# ======================
# ContentVersion
# ======================
class ContentVersion(db.Model):
    __tablename__ = "content_version"

    version_id = db.Column(db.Integer, primary_key=True)
    # 指向這個版本屬於哪個 Content
    content_id = db.Column(
        db.Integer,
        db.ForeignKey("content.content_id"),
        nullable=False,
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
    )
    version_number = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text)
    file_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ 明確指定：這個 relationship 是走 content_id 這條 FK
    content = db.relationship(
        "Content",
        back_populates="versions",
        foreign_keys=[content_id],
    )

    creator = db.relationship(
        "User",
        backref="content_versions",
        foreign_keys=[created_by],
    )


# ======================
# Tag
# ======================
class Tag(db.Model):
    __tablename__ = "tag"

    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
    )

    creator = db.relationship("User", backref="tags")


# ======================
# ContentTag（多對多關聯表）
# ======================
class ContentTag(db.Model):
    __tablename__ = "content_tag"

    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(
        db.Integer,
        db.ForeignKey("content.content_id"),
        nullable=False,
    )
    tag_id = db.Column(
        db.Integer,
        db.ForeignKey("tag.tag_id"),
        nullable=False,
    )

    content = db.relationship("Content", backref="content_tags")
    tag = db.relationship("Tag", backref="content_tags")
