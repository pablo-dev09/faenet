"""
FaeNet - Rotas /api/me
======================
Endpoints do usuario logado: dados, edicao de perfil, status online.
"""

from flask import Blueprint, request
from flask_login import current_user, login_required

from ..services import auth_service, user_service
from ..utils.responses import fail, ok

me_bp = Blueprint("me", __name__, url_prefix="/api/me")


@me_bp.route("", methods=["GET"])
@login_required
def get_me():
    return ok(current_user.to_public_dict())


@me_bp.route("", methods=["PUT", "PATCH"])
@login_required
def update_me():
    data = request.get_json(silent=True) or {}
    # Atualizacao de avatar/banner por URL (ja uploaded).
    for key in ("avatar_img", "banner_img"):
        if key in data and isinstance(data[key], str) and data[key].startswith("data:"):
            # Se o cliente mandou base64, processamos.
            from ..utils.uploads import save_base64_data_url
            category = "avatar" if key == "avatar_img" else "banner"
            url = save_base64_data_url(data[key], category)
            if not url:
                return fail("Falha ao processar imagem.", 400)
            data[key] = url

    try:
        updated = user_service.update_profile(viewer=current_user, fields=data)
    except user_service.UserError as exc:
        return fail(exc.message, exc.status)
    return ok(updated)


@me_bp.route("/online", methods=["POST"])
@login_required
def heartbeat():
    auth_service.mark_user_online(current_user.username)
    return ok({"online": True})


@me_bp.route("/uploads", methods=["POST"])
@login_required
def upload_media():
    """Upload generico para o usuario logado.

    Aceita campos ``file`` e ``category`` (avatar | banner | post | story | message).
    Retorna a URL publica para uso imediato.
    """
    from ..utils.uploads import save_upload, save_base64_data_url

    category = (request.form.get("category") or "").strip().lower()
    if category not in {"avatar", "banner", "post", "story", "message"}:
        return fail("Categoria invalida.", 400)

    # Upload via arquivo.
    if "file" in request.files:
        url = save_upload(request.files["file"], category)
        if not url:
            return fail("Arquivo invalido ou muito grande.", 400)
        return ok({"url": url})

    # Upload via base64.
    data_url = (request.form.get("data_url") or "").strip()
    if data_url:
        url = save_base64_data_url(data_url, category)
        if not url:
            return fail("Imagem invalida ou muito grande.", 400)
        return ok({"url": url})

    return fail("Nenhum arquivo enviado.", 400)
