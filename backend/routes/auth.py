"""
FaeNet - Rotas de autenticacao
==============================
Endpoints de sessao: registro, login e logout.
"""

from flask import Blueprint, request

from ..services import auth_service
from ..utils.responses import fail, ok

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = auth_service.register_user(
            username=data.get("username", ""),
            password=data.get("password", ""),
            name=data.get("name", ""),
            curso=data.get("curso") or None,
            turma=data.get("turma") or None,
        )
    except auth_service.AuthError as exc:
        return fail(exc.message, exc.status)
    return ok(user.to_public_dict(), 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = auth_service.authenticate(
            username=data.get("username", ""),
            password=data.get("password", ""),
        )
    except auth_service.AuthError as exc:
        return fail(exc.message, exc.status)
    return ok(user.to_public_dict())


@auth_bp.route("/logout", methods=["POST"])
def logout():
    auth_service.logout_current_user()
    return ok({"message": "Sessao encerrada."})
