"""
FaeNet - Utils: uploads
=======================
Helpers para salvar arquivos enviados respeitando os limites do app,
validando extensao/MIME e gerando nomes unicos. Mantem a pasta de
upload sempre dentro de ``backend/uploads/<categoria>``.
"""

import os
import secrets
from pathlib import Path
from typing import Iterable

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def allowed_image(filename: str) -> bool:
    return _ext(filename) in current_app.config["ALLOWED_IMAGE_EXT"]


def allowed_file(filename: str) -> bool:
    return _ext(filename) in current_app.config["ALLOWED_FILE_EXT"]


def save_upload(file: FileStorage, category: str) -> str | None:
    """Salva um arquivo no diretorio apropriado e retorna a URL publica.

    Retorna ``None`` se o arquivo for invalido (extensao ou categoria).
    """
    if not file or not file.filename:
        return None

    folders = current_app.config["UPLOAD_FOLDERS"]
    if category not in folders:
        return None

    ext = _ext(file.filename)
    if category in current_app.config["IMAGE_ONLY_CATEGORIES"]:
        if ext not in current_app.config["ALLOWED_IMAGE_EXT"]:
            return None
    else:
        # mensagem: aceita tanto imagem quanto arquivo
        if ext not in current_app.config["ALLOWED_IMAGE_EXT"] | current_app.config["ALLOWED_FILE_EXT"]:
            return None

    # Garante nome seguro + sufixo aleatorio.
    base = secure_filename(file.filename.rsplit(".", 1)[0]) or "file"
    random_suffix = secrets.token_hex(4)
    new_name = f"{base[:40]}_{random_suffix}.{ext}"
    dest_dir: Path = folders[category]
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / new_name
    file.save(dest)

    # Limite de tamanho (verificacao adicional apos o save).
    max_bytes = current_app.config.get("MAX_UPLOAD_BYTES", 16 * 1024 * 1024)
    if dest.stat().st_size > max_bytes:
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass
        return None

    return f"/uploads/{category}/{new_name}"


def save_base64_data_url(data_url: str, category: str, suggested_ext: str = "png") -> str | None:
    """Aceita uma data URL (data:image/png;base64,xxxx) e persiste como arquivo.

    Util para uploads via canvas (ex: avatar) ou para o frontend quando
    o navegador expoe apenas a string base64. Retorna URL publica.
    """
    import base64

    if not isinstance(data_url, str) or not data_url.startswith("data:"):
        return None

    try:
        header, b64 = data_url.split(",", 1)
    except ValueError:
        return None

    mime = header.split(";")[0].split(":", 1)[-1].lower() if ":" in header else "image/png"
    ext_map = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
        "image/gif": "gif",
    }
    ext = ext_map.get(mime, suggested_ext.lower())

    folders = current_app.config["UPLOAD_FOLDERS"]
    if category not in folders:
        return None
    if category in current_app.config["IMAGE_ONLY_CATEGORIES"]:
        if ext not in current_app.config["ALLOWED_IMAGE_EXT"]:
            return None

    try:
        data = base64.b64decode(b64)
    except (ValueError, TypeError):
        return None

    name = f"upload_{secrets.token_hex(8)}.{ext}"
    dest_dir: Path = folders[category]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name
    dest.write_bytes(data)

    max_bytes = current_app.config.get("MAX_UPLOAD_BYTES", 16 * 1024 * 1024)
    if dest.stat().st_size > max_bytes:
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass
        return None

    return f"/uploads/{category}/{name}"


def delete_upload_by_url(url: str) -> None:
    """Remove um arquivo de upload dado sua URL publica. Nao falha se ausente."""
    if not url or not url.startswith("/uploads/"):
        return
    try:
        relative = url.replace("/uploads/", "", 1)
        path = Path(current_app.config["UPLOAD_ROOT"]) / relative
        # Garante que o arquivo esta dentro do UPLOAD_ROOT.
        upload_root = Path(current_app.config["UPLOAD_ROOT"]).resolve()
        path = path.resolve()
        if str(path).startswith(str(upload_root)) and path.is_file():
            os.remove(path)
    except (OSError, ValueError):
        pass
