"""
FaeNet - Rotas de Pagina
========================
Cada rota serve o template HTML da SPA. A renderizacao do conteudo
eh feita no cliente via JavaScript consumindo a API REST.
"""

from pathlib import Path

from flask import Blueprint, abort, current_app, make_response, send_from_directory

pages_bp = Blueprint("pages", __name__)

# Caminho da pasta de frontend (um nivel acima de backend/).
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


def _no_cache(response):
    """Anexa headers para impedir cache em desenvolvimento.

    Evita que o navegador fique com CSS/JS antigo apos um fix.
    Em producao, configure cache proprio (CDN/Expires) e remova isto.
    """
    if current_app.config.get("DEBUG"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


def _serve(name: str):
    """Envia um arquivo da pasta frontend com fallback para index.html (SPA)."""
    target = FRONTEND_DIR / name
    if not target.exists():
        abort(404)
    response = make_response(send_from_directory(FRONTEND_DIR, name))
    return _no_cache(response)


@pages_bp.route("/", methods=["GET"])
def root():
    """A raiz mostra a landing (ou redireciona para /login via JS)."""
    return _serve("index.html")


@pages_bp.route("/<path:filename>", methods=["GET"])
def static_proxy(filename: str):
    """Serve arquivos estaticos do frontend (HTML, CSS, JS).

    Para qualquer rota que nao bata em /api, /uploads ou /static,
    devolve o index.html (SPA fallback - o router do cliente decide).
    """
    if not filename:
        return _serve("index.html")

    target = FRONTEND_DIR / filename
    if target.is_file():
        response = make_response(send_from_directory(FRONTEND_DIR, filename))
        return _no_cache(response)

    # SPA fallback: o cliente cuida do roteamento.
    return _serve("index.html")
