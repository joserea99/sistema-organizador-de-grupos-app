from flask import Blueprint, jsonify, session

api_bp = Blueprint("api", __name__)


@api_bp.route("/test")
def test():
    return jsonify(
        {"status": "API funcionando", "user": session.get("username", "No autenticado")}
    )
