"""
FaeNet - Model: HubItem
=======================
Itens do Hub do Curso. Estrutura polimorfica distinguida por
``item_type``: 'estagio', 'prova', 'forum_topic', 'forum_answer'.
Campos especificos de cada tipo vao em ``extra`` (JSON).
"""

import json
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db


# Tipos validos de item_type
ITEM_TYPE_ESTAGIO = "estagio"
ITEM_TYPE_PROVA = "prova"
ITEM_TYPE_FORUM_TOPIC = "forum_topic"
ITEM_TYPE_FORUM_ANSWER = "forum_answer"
ITEM_TYPES = {
    ITEM_TYPE_ESTAGIO,
    ITEM_TYPE_PROVA,
    ITEM_TYPE_FORUM_TOPIC,
    ITEM_TYPE_FORUM_ANSWER,
}


def _new_id() -> str:
    return f"h{uuid.uuid4().hex[:8]}"


class HubItem(db.Model):
    """Item polimorfico do Hub do Curso."""

    __tablename__ = "hub_items"

    id = db.Column(String(24), primary_key=True, default=_new_id)
    curso = db.Column(String(80), nullable=False, index=True)
    item_type = db.Column(String(20), nullable=False, index=True)
    parent_id = db.Column(String(24), ForeignKey("hub_items.id", ondelete="CASCADE"), nullable=True, index=True)
    username = db.Column(String(60), ForeignKey("users.username", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(String(200), nullable=True)
    content = db.Column(Text, nullable=True)
    extra_json = db.Column(Text, nullable=True)
    solved = db.Column(Boolean, default=False, nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    author = relationship("User", back_populates="hub_items", foreign_keys=[username])

    # Respostas do forum: topico -> respostas
    answers = relationship(
        "HubItem",
        backref=db.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        single_parent=True,
        foreign_keys=[parent_id],
    )

    # --- Helpers ---
    @property
    def extra(self) -> dict:
        if not self.extra_json:
            return {}
        try:
            return json.loads(self.extra_json)
        except (TypeError, ValueError):
            return {}

    @extra.setter
    def extra(self, value: dict | None) -> None:
        if value is None:
            self.extra_json = None
        else:
            self.extra_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "curso": self.curso,
            "item_type": self.item_type,
            "parent_id": self.parent_id,
            "username": self.username,
            "title": self.title or "",
            "content": self.content or "",
            "extra": self.extra,
            "solved": bool(self.solved),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "author": self.author.to_public_dict() if self.author else None,
            "answers_count": len(self.answers) if self.answers is not None else 0,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<HubItem {self.id} {self.item_type} in {self.curso}>"
