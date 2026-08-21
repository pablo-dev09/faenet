"""
FaeNet - Service: notificacoes
==============================
Listagem e marcacao de leitura das notificacoes do usuario.
"""

from ..extensions import db
from ..models import Notification, User


def list_notifications(viewer: User, limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 100))
    rows = (
        Notification.query.filter_by(to_user=viewer.username)
        .order_by(Notification.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [n.to_dict() for n in rows]


def unread_count(viewer: User) -> int:
    return Notification.query.filter_by(to_user=viewer.username, read=False).count()


def mark_all_read(viewer: User) -> int:
    updated = (
        Notification.query.filter_by(to_user=viewer.username, read=False)
        .update({"read": True})
    )
    if updated:
        db.session.commit()
    return updated


def mark_one_read(viewer: User, notif_id: str) -> bool:
    n = Notification.query.filter_by(id=notif_id, to_user=viewer.username).first()
    if not n:
        return False
    n.read = True
    db.session.commit()
    return True
