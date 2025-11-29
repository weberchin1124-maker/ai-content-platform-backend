from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Project, ProjectMember

project_bp = Blueprint("project", __name__)

@project_bp.route("", methods=["GET"])
@jwt_required()
def list_projects():
    user_id = get_jwt_identity()

    memberships = ProjectMember.query.filter_by(user_id=user_id).all()
    projects = [m.project for m in memberships]

    result = []
    for p in projects:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "owner_id": p.owner_id
        })

    return jsonify(result), 200


@project_bp.route("", methods=["POST"])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json() or {}

    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"message": "專案名稱必填"}), 400

    project = Project(name=name, description=description, owner_id=user_id)
    db.session.add(project)
    db.session.flush()  # 先拿到 project.id

    member = ProjectMember(
        project_id=project.id,
        user_id=user_id,
        role="owner"
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "owner_id": project.owner_id
    }), 201
