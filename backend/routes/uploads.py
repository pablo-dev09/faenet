"""
FaeNet - Rotas de uploads
=========================
Serve os arquivos gravados em ``backend/uploads/<categoria>`` atraves
de URLs publicas como ``/uploads/avatars/xxx.png``. O caminho eh
validado para impedir traversal (acesso fora de ``UPLOAD_ROOT``).
"""

from pathlib import Path

from flask import Blueprint, abort, current_app, send_from_directory

uploads_bp = Blueprint("uploads", __name__, url_prefix="/uploads")


@uploads_bp.route("/<category>/<path:filename>", methods=["GET"])
def serve_upload(category: str, filename: str):
    folders: dict = current_app.config["UPLOAD_FOLDERS"]
    if category not in folders:
        abort(404)

    folder: Path = folders[category]
    if not folder.exists():
        abort(404)

    # Bloqueia tentativa de traversal.
    safe_name = Path(filename).name
    target = folder / safe_name
    try:
        target = target.resolve()
        folder_resolved = folder.resolve()
        if not str(target).startswith(str(folder_resolved)):
            abort(404)
    except (OSError, RuntimeError):
        abort(404)

    if not target.is_file():
        abort(404)

    return send_from_directory(folder, safe_name)
