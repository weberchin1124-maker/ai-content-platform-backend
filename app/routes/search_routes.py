#簡單搜尋 API：title + prompt 用 SQL ILIKE 查
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from ..extensions import db
from ..models import (
    ProjectMember,
    Content,
    ContentVersion,
)

search_bp = Blueprint("search", __name__)


@search_bp.route("", methods=["GET"])
@jwt_required()
def search_contents():
    """
    簡單搜尋：
    - 在 content.title
    - 以及最新版本的 prompt
    做 ILIKE 關鍵字查詢
    """
    user_id = get_jwt_identity()
    query = (request.args.get("q") or "").strip()

    if not query:
        return jsonify({"message": "請提供 q 參數作為搜尋關鍵字"}), 400

    # 找出使用者有參與的專案 id
    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    project_ids = [m.project_id for m in memberships]
    if not project_ids:
        return jsonify([]), 200

    # JOIN content & content_version（只取最新版本）
    q = (
        db.session.query(Content, ContentVersion)
        .join(
            ContentVersion,
            Content.latest_version_id == ContentVersion.version_id,
            isouter=True
        )
        .filter(Content.project_id.in_(project_ids))
        .filter(
            or_(
                Content.title.ilike(f"%{query}%"),
                ContentVersion.prompt.ilike(f"%{query}%")
            )
        )
        .order_by(Content.created_at.desc())
        .limit(50)
    )

    results = []
    for content, version in q.all():
        results.append({
            "content_id": content.content_id,
            "title": content.title,
            "project_id": content.project_id,
            "primary_type": content.primary_type,
            "latest_version": {
                "version_id": version.version_id if version else None,
                "version_number": version.version_number if version else None,
                "prompt": version.prompt if version else None,
            },
        })

    return jsonify(results), 200
