"""
FaeNet - Service: mensagens
==========================
Conversas privadas entre usuarios. As mensagens sao sempre
direcionadas (from_user -> to_user); o feed do chat eh montado
agregando mensagens nos dois sentidos.
"""

from collections import defaultdict
from datetime import datetime

from ..extensions import db
from ..models import Message, Notification, User
from ..utils.security import sanitize_text


class MessageError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def list_conversations(viewer: User) -> list[dict]:
    """Retorna o resumo das conversas (ultima mensagem, contadores)."""
    rows = (
        Message.query.filter(
            (Message.from_user == viewer.username) | (Message.to_user == viewer.username)
        )
        .order_by(Message.timestamp.desc())
        .all()
    )

    grouped: dict[str, list[Message]] = defaultdict(list)
    for m in rows:
        other = m.to_user if m.from_user == viewer.username else m.from_user
        grouped[other].append(m)

    conversations = []
    for other_username, msgs in grouped.items():
        other = User.query.get(other_username)
        if not other:
            continue
        last = msgs[0]
        unread = sum(1 for m in msgs if m.to_user == viewer.username and not m.read)
        conversations.append({
            "with": other.to_public_dict(),
            "last_message": last.to_dict(),
            "unread_count": unread,
        })
    # Ordena pela ultima mensagem.
    conversations.sort(key=lambda c: c["last_message"]["timestamp"] or "", reverse=True)
    return conversations


def get_thread(viewer: User, other_username: str, limit: int = 100, before: str | None = None) -> list[dict]:
    other = User.query.get(other_username.lower() if other_username else "")
    if not other:
        raise MessageError("Usuario nao encontrado.", 404)
    if other.username == viewer.username:
        raise MessageError("Voce nao pode abrir conversa com voce mesmo.", 400)

    limit = max(1, min(limit, 200))
    query = Message.query.filter(
        ((Message.from_user == viewer.username) & (Message.to_user == other.username))
        | ((Message.from_user == other.username) & (Message.to_user == viewer.username))
    )
    if before:
        try:
            before_dt = datetime.fromisoformat(before)
            query = query.filter(Message.timestamp < before_dt)
        except ValueError:
            pass
    messages = query.order_by(Message.timestamp.desc()).limit(limit).all()
    messages.reverse()
    return [m.to_dict() for m in messages]


def send_message(
    *,
    sender: User,
    to_user: str,
    text: str | None,
    file_url: str | None = None,
    file_name: str | None = None,
    file_type: str | None = None,
    reply_to: dict | None = None,
) -> Message:
    recipient = User.query.get(to_user.lower() if to_user else "")
    if not recipient:
        raise MessageError("Destinatario nao encontrado.", 404)
    if recipient.username == sender.username:
        raise MessageError("Voce nao pode enviar mensagem para voce mesmo.", 400)

    text = sanitize_text(text) if text else ""
    if not text and not file_url:
        raise MessageError("Mensagem vazia.", 400)
    if len(text) > 4000:
        raise MessageError("Mensagem muito longa.", 400)

    message = Message(
        from_user=sender.username,
        to_user=recipient.username,
        text=text or None,
        file_url=file_url,
        file_name=file_name,
        file_type=file_type,
    )
    message.reply_to = reply_to
    db.session.add(message)

    # Notificacao para o destinatario.
    preview = text[:80] if text else ("📎 Arquivo" if file_type == "file" else "🖼️ Imagem")
    notif = Notification(
        to_user=recipient.username,
        from_name=sender.name,
        from_avatar_text=sender.avatar_initials(),
        from_avatar_img=sender.avatar_img,
        notif_type="message",
        text=f"{sender.name}: {preview}",
        meta_json=None,
    )
    db.session.add(notif)
    db.session.commit()
    return message


def mark_thread_read(viewer: User, other_username: str) -> int:
    """Marca como lidas todas as mensagens recebidas do outro usuario."""
    updated = (
        Message.query.filter_by(from_user=other_username, to_user=viewer.username, read=False)
        .update({"read": True})
    )
    if updated:
        db.session.commit()
    return updated
