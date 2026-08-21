"""
FaeNet - Utils: respostas JSON
==============================
Helpers para padronizar retornos da API. Mantem a API consistente
e desacopla os blueprints do Flask ``jsonify`` direto.
"""

from typing import Any

from flask import jsonify


def ok(data: Any = None, status: int = 200):
    """Resposta de sucesso padronizada: ``{"ok": true, "data": ...}``."""
    payload = {"ok": True, "data": data}
    return jsonify(payload), status


def fail(message: str, status: int = 400, code: str | None = None, extra: dict | None = None):
    """Resposta de erro padronizada: ``{"ok": false, "error": ...}``."""
    err: dict[str, Any] = {"message": message}
    if code:
        err["code"] = code
    if extra:
        err["extra"] = extra
    return jsonify({"ok": False, "error": err}), status
