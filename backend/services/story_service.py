"""
FaeNet - Service: stories
=========================
Stories com expiracao de 24h. A verificacao de expiracao acontece em
tempo de consulta (story.is_expired) e na limpeza, sem job em background.
"""

from datetime import datetime, timedelta

from ..extensions import db
from ..models import Story, User, story_viewers
from ..utils.security import MAX_CAPTION_LEN, sanitize_text


STORY_TTL_HOURS = 24


class StoryError(Exception):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def cleanup_expired() -> int:
    """Remove stories expirados. Retorna a quantidade removida."""
    cutoff = datetime.utcnow() - timedelta(hours=STORY_TTL_HOURS)
    expired = Story.query.filter(Story.timestamp < cutoff).all()
    count = len(expired)
    for s in expired:
        db.session.delete(s)
    if count:
        db.session.commit()
    return count


def list_active(viewer: User) -> list[dict]:
    cutoff = datetime.utcnow() - timedelta(hours=STORY_TTL_HOURS)
    stories = (
        Story.query.filter(Story.timestamp >= cutoff)
        .order_by(Story.timestamp.desc())
        .all()
    )
    # Apenas stories de quem o usuario segue + os proprios.
    following_ids = {u.username for u in viewer.followed} if viewer.followed else set()
    following_ids.add(viewer.username)
    stories = [s for s in stories if s.username in following_ids]
    return [s.to_dict(current_user=viewer.username) for s in stories]


def create_story(*, author: User, image_url: str, caption: str | None = None) -> Story:
    if not image_url:
        raise StoryError("Imagem obrigatoria.", 400)
    story = Story(
        username=author.username,
        image=image_url,
        caption=(sanitize_text(caption)[:MAX_CAPTION_LEN] if caption else None),
    )
    db.session.add(story)
    db.session.commit()
    return story


def delete_story(*, viewer: User, story_id: str) -> None:
    story = Story.query.get(story_id)
    if not story:
        raise StoryError("Story nao encontrado.", 404)
    if story.username != viewer.username and not viewer.is_admin:
        raise StoryError("Voce nao pode apagar esse story.", 403)
    db.session.delete(story)
    db.session.commit()


def mark_viewed(*, viewer: User, story_id: str) -> None:
    story = Story.query.get(story_id)
    if not story or story.username == viewer.username:
        return
    exists = db.session.query(story_viewers).filter_by(user_id=viewer.username, story_id=story_id).first()
    if exists:
        return
    db.session.execute(
        story_viewers.insert().values(user_id=viewer.username, story_id=story_id)
    )
    db.session.commit()
