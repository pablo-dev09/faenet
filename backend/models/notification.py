"""
FaeNet - Model: Notification
============================
Notificacoes de interacoes: like, comment, follow, message.
Mantemos snapshot do autor no momento da geracao para o feed
de notificacoes continuar exibindo dados coerentes mesmo se o
usuario mudar nome/avatar.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ..extensions import db


def _new_id() -> str:
    return f"n{uuid.uuid4().hex[:8]}"


class Notification(db.Model):
    """Notificacao entregue a um usuario."""

    __tablename__ = "notifications"

    id = db.Column(String(24), primary_key=True, default=_new_id)
    to_user = db.Column(String(60), ForeignKey("users.username", ondelete="CASCADE"), nullable=False, index=True)
    from_name = db.Column(String(120), nullable=False)
    from_avatar_text = db.Column(String(4), nullable=True)
    from_avatar_img = db.Column(String(500), nullable=True)
    notif_type = db.Column(String(30), nullable=False)  # like | comment | follow | message
    text = db.Column(String(200), nullable=False)
    read = db.Column(Boolean, default=False, nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Payload opcional (ex: post_id para acoes de like/comment)
    meta_json = db.Column(String(500), nullable=True)

    recipient = relationship("User", back_populates="notifications", foreign_keys=[to_user])

    def to_dict(self) -> dict:
        import json
        meta = None
        if self.meta_json:
            try:
                meta = json.loads(self.meta_json)
            except (TypeError, ValueError):
                meta = None
        return {
            "id": self.id,
            "to_user": self.to_user,
            "from_name": self.from_name,
            "from_avatar_text": self.from_avatar_text,
            "from_avatar_img": self.from_avatar_img,
            "type": self.notif_type,
            "text": self.text,
            "read": bool(self.read),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "meta": meta,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Notification {self.id} -> {self.to_user} ({self.notif_type})>"
