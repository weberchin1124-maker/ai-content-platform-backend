# Content 的 API 範例（建立＋列表）
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import (
    Project,
    ProjectMember,
    Content,
    ContentVersion,
)

content_bp = Blueprint("content", __name__)


def _user_in_project(user_id, project_id):
    return (
        ProjectMember.query
        .filter_by(user_id=user_id, project_id=project_id)
        .first()
        is not None
    )


@content_bp.route("/project/<int:project_id>", methods=["GET"])
@jwt_required()
def list_project_contents(project_id):
    user_id = get_jwt_identity()

    if not _user_in_project(user_id, project_id):
        return jsonify({"message": "你沒有這個專案的權限"}), 403

    contents = (
        Content.query.filter_by(project_id=project_id)
        .order_by(Content.created_at.desc())
        .all()
    )

    result = []
    for c in contents:
        latest = c.latest_version
        result.append({
            "content_id": c.content_id,
            "title": c.title,
            "primary_type": c.primary_type,
            "source_tool": c.source_tool,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "latest_version": {
                "version_id": latest.version_id if latest else None,
                "version_number": latest.version_number if latest else None,
            },
        })

    return jsonify(result), 200


@content_bp.route("/project/<int:project_id>", methods=["POST"])
@jwt_required()
def create_content_with_first_version(project_id):
    """
    建立一筆 content + 第一個 content_version
    body 範例：
    {
      "title": "模型測試一次",
      "primary_type": "text",
      "source_tool": "ChatGPT",
      "prompt": "幫我寫一段介紹...",
      "file_url": null
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    if not _user_in_project(user_id, project_id):
        return jsonify({"message": "你沒有這個專案的權限"}), 403

    title = data.get("title")
    primary_type = data.get("primary_type", "text")
    source_tool = data.get("source_tool")
    prompt = data.get("prompt")
    file_url = data.get("file_url")

    if not title:
        return jsonify({"message": "title 必填"}), 400

    # 1. 建立 content
    content = Content(
        project_id=project_id,
        creator_user_id=user_id,
        title=title,
        primary_type=primary_type,
        source_tool=source_tool,
    )
    db.session.add(content)
    db.session.flush()  # 先拿到 content_id

    # 2. 建立第一個版本（version_number = 1）
    version = ContentVersion(
        content_id=content.content_id,
        created_by=user_id,
        version_number=1,
        prompt=prompt,
        file_url=file_url,
        # response_ref 目前可先留空，之後接 NoSQL 再補
    )
    db.session.add(version)
    db.session.flush()

    # 3. 更新 content.latest_version_id
    content.latest_version_id = version.version_id

    db.session.commit()

    return jsonify({
        "content_id": content.content_id,
        "title": content.title,
        "primary_type": content.primary_type,
        "source_tool": content.source_tool,
        "version": {
            "version_id": version.version_id,
            "version_number": version.version_number,
        },
    }), 201

