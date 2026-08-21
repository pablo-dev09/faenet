"""
FaeNet - Service: Hub do Curso
==============================
Itens polimorficos: estagios, provas, forum de duvidas (topicos + respostas).
"""

from ..extensions import db
from ..models import HubItem, ITEM_TYPES
from ..utils.security import sanitize_text


class HubError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def list_items(*, curso: str | None, item_type: str, limit: int = 50, offset: int = 0) -> list[dict]:
    if item_type not in ITEM_TYPES:
        raise HubError("Tipo de item invalido.", 400)
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    query = HubItem.query.filter_by(item_type=item_type)
    if curso:
        query = query.filter_by(curso=curso)

    if item_type == "forum_topic":
        # Apenas topicos raiz (sem parent).
        query = query.filter(HubItem.parent_id.is_(None))
    elif item_type == "forum_answer":
        # Apenas respostas (com parent). Se curso nao for passado,
        # este filtro retorna mesmo assim (mas caller deve informar).
        query = query.filter(HubItem.parent_id.isnot(None))

    items = query.order_by(HubItem.timestamp.desc()).offset(offset).limit(limit).all()
    return [i.to_dict() for i in items]


def get_item(item_id: str) -> dict:
    item = HubItem.query.get(item_id)
    if not item:
        raise HubError("Item nao encontrado.", 404)
    return item.to_dict()


def list_answers(topic_id: str) -> list[dict]:
    topic = HubItem.query.get(topic_id)
    if not topic or topic.item_type != "forum_topic":
        raise HubError("Topico nao encontrado.", 404)
    return [a.to_dict() for a in sorted(topic.answers, key=lambda a: a.timestamp)]


def create_item(*, author, item_type: str, curso: str, title: str | None = None, content: str | None = None, extra: dict | None = None) -> HubItem:
    if item_type not in ITEM_TYPES:
        raise HubError("Tipo de item invalido.", 400)
    if item_type == "forum_answer":
        raise HubError("Use ``reply_topic`` para responder um topico.", 400)

    curso = sanitize_text(curso)[:80]
    if not curso:
        raise HubError("Curso obrigatorio.", 400)

    title_clean = sanitize_text(title)[:200] if title else None
    content_clean = sanitize_text(content)[:8000] if content else None

    if item_type in {"estagio", "prova", "forum_topic"}:
        if not title_clean:
            raise HubError("Titulo obrigatorio.", 400)

    extra_clean: dict = {}
    if isinstance(extra, dict):
        for k, v in extra.items():
            extra_clean[str(k)[:80]] = sanitize_text(str(v))[:500] if v is not None else None

    item = HubItem(
        curso=curso,
        item_type=item_type,
        username=author.username,
        title=title_clean,
        content=content_clean,
    )
    item.extra = extra_clean
    db.session.add(item)
    db.session.commit()
    return item


def reply_topic(*, author, topic_id: str, content: str) -> HubItem:
    topic = HubItem.query.get(topic_id)
    if not topic or topic.item_type != "forum_topic":
        raise HubError("Topico nao encontrado.", 404)
    content_clean = sanitize_text(content)
    if not content_clean:
        raise HubError("Resposta vazia.", 400)
    answer = HubItem(
        curso=topic.curso,
        item_type="forum_answer",
        parent_id=topic.id,
        username=author.username,
        content=content_clean,
    )
    db.session.add(answer)
    db.session.commit()
    return answer


def update_item(*, viewer, item_id: str, fields: dict) -> dict:
    item = HubItem.query.get(item_id)
    if not item:
        raise HubError("Item nao encontrado.", 404)
    if item.username != viewer.username and not viewer.is_admin:
        raise HubError("Voce nao pode editar esse item.", 403)
    if "title" in fields:
        item.title = sanitize_text(fields.get("title") or "")[:200] or None
    if "content" in fields:
        item.content = sanitize_text(fields.get("content") or "")[:8000] or None
    if "extra" in fields and isinstance(fields["extra"], dict):
        item.extra = fields["extra"]
    db.session.commit()
    return item.to_dict()


def delete_item(*, viewer, item_id: str) -> None:
    item = HubItem.query.get(item_id)
    if not item:
        raise HubError("Item nao encontrado.", 404)
    if item.username != viewer.username and not viewer.is_admin:
        raise HubError("Voce nao pode apagar esse item.", 403)
    db.session.delete(item)
    db.session.commit()


def mark_solved(*, viewer, topic_id: str, solved: bool) -> dict:
    topic = HubItem.query.get(topic_id)
    if not topic or topic.item_type != "forum_topic":
        raise HubError("Topico nao encontrado.", 404)
    if topic.username != viewer.username and not viewer.is_admin:
        raise HubError("Apenas o autor pode marcar como resolvido.", 403)
    topic.solved = bool(solved)
    db.session.commit()
    return topic.to_dict()
