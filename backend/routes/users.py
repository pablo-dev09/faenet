"""
FaeNet - Rotas /api/users
=========================
Perfil publico, busca, seguir/deixar de seguir, sugestoes.
"""

from flask import Blueprint, request
from flask_login import current_user, login_required

from ..services import post_service, user_service
from ..utils.responses import fail, ok

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@login_required
def search():
    query = (request.args.get("q") or "").strip()
    if not query:
        return ok([])
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
    return ok(user_service.search_users(current_user, query, limit=limit))


@users_bp.route("/suggestions", methods=["GET"])
@login_required
def suggestions():
    try:
        limit = int(request.args.get("limit", 8))
    except ValueError:
        limit = 8
    return ok(user_service.suggest_users(current_user, limit=limit))


@users_bp.route("/online", methods=["GET"])
@login_required
def online():
    try:
        limit = int(request.args.get("limit", 30))
    except ValueError:
        limit = 30
    return ok(user_service.list_online_users(limit=limit))


@users_bp.route("/<username>", methods=["GET"])
@login_required
def profile(username: str):
    try:
        data = user_service.get_profile(current_user, username)
    except user_service.UserError as exc:
        return fail(exc.message, exc.status)
    return ok(data)


@users_bp.route("/<username>/posts", methods=["GET"])
@login_required
def user_posts(username: str):
    try:
        limit = int(request.args.get("limit", 30))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        limit, offset = 30, 0
    posts = post_service.list_user_posts(current_user, username, limit=limit, offset=offset)
    return ok(posts)


@users_bp.route("/<username>/follow", methods=["POST"])
@login_required
def follow(username: str):
    try:
        result = user_service.follow_user(current_user, username)
    except user_service.UserError as exc:
        return fail(exc.message, exc.status)
    return ok(result)


@users_bp.route("/<username>/follow", methods=["DELETE"])
@login_required
def unfollow(username: str):
    try:
        result = user_service.unfollow_user(current_user, username)
    except user_service.UserError as exc:
        return fail(exc.message, exc.status)
    return ok(result)


@users_bp.route("/<username>/followers", methods=["GET"])
@login_required
def followers(username: str):
    try:
        return ok(user_service.list_followers(current_user, username))
    except user_service.UserError as exc:
        return fail(exc.message, exc.status)


@users_bp.route("/<username>/following", methods=["GET"])
@login_required
def following(username: str):
    try:
        return ok(user_service.list_following(current_user, username))
    except user_service.UserError as exc:
        return fail(exc.message, exc.status)
