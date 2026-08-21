"""
FaeNet - Rotas /api/notifications
=================================
Listagem e marcacao de leitura.
"""

from flask import Blueprint, request
from flask_login import current_user, login_required

from ..services import notification_service
from ..utils.responses import fail, ok

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("", methods=["GET"])
@login_required
def list_notifications():
    try:
        limit = int(request.args.get("limit", 50))
    except ValueError:
        limit = 50
    return ok({
        "items": notification_service.list_notifications(current_user, limit=limit),
        "unread_count": notification_service.unread_count(current_user),
    })


@notifications_bp.route("/read", methods=["POST"])
@login_required
def mark_all_read():
    n = notification_service.mark_all_read(current_user)
    return ok({"updated": n})


@notifications_bp.route("/<notif_id>/read", methods=["POST"])
@login_required
def mark_one(notif_id: str):
    ok_flag = notification_service.mark_one_read(current_user, notif_id)
    if not ok_flag:
        return fail("Notificacao nao encontrada.", 404)
    return ok({"updated": True})
