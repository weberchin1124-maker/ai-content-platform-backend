# app/routes/project_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Project, ProjectMember

project_bp = Blueprint("projects", __name__)

@project_bp.route("", methods=["POST"])  # ✅ 或改成 "/" 也可以
@jwt_required()
def create_project():
    user_id = get_jwt_identity()

    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"message": "專案名稱必填"}), 400

    project = Project(
        name=name,
        description=description,
        owner_id=user_id,
    )
    db.session.add(project)
    db.session.flush()  # 這時候 project.project_id 會有值

    member = ProjectMember(
        project_id=project.project_id,  # ✅ 這裡一定要用 project.project_id
        user_id=user_id,
        role="owner",
    )
    db.session.add(member)
    db.session.commit()

    return jsonify(
        {
            "id": project.project_id,
            "name": project.name,
            "description": project.description,
            "owner_id": project.owner_id,
        }
    ), 201
