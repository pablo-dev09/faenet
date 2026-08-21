"""
FaeNet - Utils: seguranca
=========================
Validacoes e sanitizacoes de entrada. Centralizar aqui facilita a
auditoria de seguranca e a evolucao das regras sem tocar nos blueprints.
"""

import re
import unicodedata

# Username: letras, numeros, underscore e ponto. 3..30 chars.
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,30}$")
# Senha minima: 6 caracteres (ajustavel). Nao exigimos complexidade alta
# para nao bloquear usuarios novos; hash seguro ja protege a credencial.
MIN_PASSWORD_LEN = 6
MAX_PASSWORD_LEN = 128
# Limite de tamanho para textos longos (post, mensagem, bio, etc.)
MAX_TEXT_LEN = 4000
MAX_BIO_LEN = 280
MAX_CAPTION_LEN = 200
MAX_TITLE_LEN = 200
MAX_NAME_LEN = 120
MAX_CURSO_LEN = 80
MAX_TURMA_LEN = 100


def is_valid_username(value: str) -> bool:
    return bool(value) and bool(USERNAME_RE.match(value))


def is_valid_password(value: str) -> bool:
    if not isinstance(value, str):
        return False
    return MIN_PASSWORD_LEN <= len(value) <= MAX_PASSWORD_LEN


def is_safe_text(value: str, max_len: int = MAX_TEXT_LEN) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    return 0 <= len(value) <= max_len


def sanitize_text(value: str | None) -> str:
    """Remove caracteres de controle e normaliza espacos. Nao altera HTML
    (o frontend ja lida com a renderizacao segura via ``textContent``)."""
    if value is None:
        return ""
    # Remove caracteres de controle (exceto \\n e \\t).
    cleaned = "".join(
        ch for ch in value
        if unicodedata.category(ch)[0] != "C" or ch in "\n\t"
    )
    # Normaliza multiplos espacos (mas mantem quebras de linha).
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def safe_filename(name: str) -> str:
    """Normaliza um nome de arquivo removendo caracteres perigosos."""
    if not name:
        return "file"
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:120] or "file"
