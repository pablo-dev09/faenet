"""
FaeNet - Rotas /api/messages
============================
Conversas, historico, envio com anexo, marcacao de leitura.
"""

from flask import Blueprint, request
from flask_login import current_user, login_required

from ..services import message_service
from ..utils.responses import fail, ok
from ..utils.uploads import save_base64_data_url, save_upload

messages_bp = Blueprint("messages", __name__, url_prefix="/api/messages")


@messages_bp.route("", methods=["GET"])
@login_required
def conversations():
    return ok(message_service.list_conversations(current_user))


@messages_bp.route("/<username>", methods=["GET"])
@login_required
def thread(username: str):
    try:
        limit = int(request.args.get("limit", 100))
    except ValueError:
        limit = 100
    before = request.args.get("before")
    try:
        msgs = message_service.get_thread(current_user, username, limit=limit, before=before)
    except message_service.MessageError as exc:
        return fail(exc.message, exc.status)
    # Ao abrir a conversa, marca como lida.
    message_service.mark_thread_read(current_user, username)
    return ok(msgs)


@messages_bp.route("", methods=["POST"])
@login_required
def send():
    """Envia uma mensagem. Suporta JSON e multipart (com arquivo)."""
    file_url = None
    file_name = None
    file_type = None
    text = None
    to_user = None
    reply_to = None

    if request.is_json:
        data = request.get_json(silent=True) or {}
        to_user = data.get("to_user")
        text = data.get("text")
        file_url = data.get("file_url")
        file_name = data.get("file_name")
        file_type = data.get("file_type")
        reply_to = data.get("reply_to")
        # Caso o cliente envie a imagem em base64.
        if not file_url and data.get("file_data_url"):
            kind = data.get("file_type") or "file"
            category = "message"
            file_url = save_base64_data_url(data["file_data_url"], category)
            if file_url and not file_type:
                file_type = "image" if (data["file_data_url"].startswith("data:image")) else "file"
    else:
        to_user = request.form.get("to_user")
        text = request.form.get("text")
        reply_raw = request.form.get("reply_to")
        if reply_raw:
            import json
            try:
                reply_to = json.loads(reply_raw)
            except ValueError:
                reply_to = None
        if "file" in request.files:
            f = request.files["file"]
            url = save_upload(f, "message")
            if url:
                file_url = url
                file_name = f.filename
                # Decide pelo mime/extensao se foi imagem ou arquivo.
                ct = (f.mimetype or "").lower()
                file_type = "image" if ct.startswith("image/") else "file"

    if not to_user:
        return fail("Destinatario obrigatorio.", 400)

    try:
        message = message_service.send_message(
            sender=current_user,
            to_user=to_user,
            text=text,
            file_url=file_url,
            file_name=file_name,
            file_type=file_type,
            reply_to=reply_to,
        )
    except message_service.MessageError as exc:
        return fail(exc.message, exc.status)
    return ok(message.to_dict(), 201)


@messages_bp.route("/<username>/read", methods=["POST"])
@login_required
def mark_read(username: str):
    n = message_service.mark_thread_read(current_user, username)
    return ok({"updated": n})
