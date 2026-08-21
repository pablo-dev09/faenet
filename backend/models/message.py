"""
FaeNet - Model: Message
=======================
Mensagens privadas entre dois usuarios. Suporta texto, imagem,
arquivo generico e resposta a uma mensagem especifica.
"""

import json
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..extensions import db


def _new_id() -> str:
    return f"m{uuid.uuid4().hex[:8]}"


class Message(db.Model):
    """Mensagem privada trocada entre dois usuarios."""

    __tablename__ = "messages"

    id = db.Column(String(24), primary_key=True, default=_new_id)
    from_user = db.Column(String(60), ForeignKey("users.username", ondelete="CASCADE"), nullable=False, index=True)
    to_user = db.Column(String(60), ForeignKey("users.username", ondelete="CASCADE"), nullable=False, index=True)
    text = db.Column(Text, nullable=True)

    file_url = db.Column(Text, nullable=True)
    file_name = db.Column(String(200), nullable=True)
    file_type = db.Column(String(20), nullable=True)  # 'image' | 'file' | None

    # Resposta a uma mensagem especifica. Guardamos o snapshot para
    # evitar lookups extras em mensagens muito antigas.
    reply_to_json = db.Column(Text, nullable=True)

    read = db.Column(Boolean, default=False, nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    sender = relationship("User", back_populates="messages_sent", foreign_keys=[from_user])
    # Sem backref para destinatario (a consulta parte sempre do usuario logado).

    # --- Helpers ---
    @property
    def reply_to(self) -> dict | None:
        if not self.reply_to_json:
            return None
        try:
            return json.loads(self.reply_to_json)
        except (TypeError, ValueError):
            return None

    @reply_to.setter
    def reply_to(self, value: dict | None) -> None:
        if value is None:
            self.reply_to_json = None
        else:
            self.reply_to_json = json.dumps(value)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from_user": self.from_user,
            "to_user": self.to_user,
            "text": self.text or "",
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "reply_to": self.reply_to,
            "read": bool(self.read),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Message {self.id} {self.from_user}->{self.to_user}>"
