"""
FaeNet - Entry point
====================
Permite executar a aplicacao com ``python app.py`` durante o
desenvolvimento. Em producao, utilize Gunicorn apontando para
``backend.app:app``.
"""

from backend.app import app

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
