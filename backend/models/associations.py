"""
FaeNet - Tabelas de Associacao
==============================
Relacionamentos muitos-para-muitos entre as entidades principais.
Usamos tabelas explicitas (em vez de ``secondary=``) porque precisamos
armazenar metadados adicionais (ex: timestamp) e facilidade de consulta.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table

from ..extensions import db


# followers: usuario (follower) -> usuario (followed)
followers = Table(
    "followers",
    db.metadata,
    Column("follower_id", String(60), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True),
    Column("followed_id", String(60), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True),
    Column("timestamp", DateTime, default=datetime.utcnow, nullable=False),
)


# post_likes: usuario curtiu publicacao
post_likes = Table(
    "post_likes",
    db.metadata,
    Column("user_id", String(60), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True),
    Column("post_id", String(24), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("timestamp", DateTime, default=datetime.utcnow, nullable=False),
)


# post_saves: usuario salvou publicacao
post_saves = Table(
    "post_saves",
    db.metadata,
    Column("user_id", String(60), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True),
    Column("post_id", String(24), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("timestamp", DateTime, default=datetime.utcnow, nullable=False),
)


# post_reposts: usuario repostou publicacao
post_reposts = Table(
    "post_reposts",
    db.metadata,
    Column("user_id", String(60), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True),
    Column("post_id", String(24), ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("timestamp", DateTime, default=datetime.utcnow, nullable=False),
)


# story_viewers: usuario visualizou story
story_viewers = Table(
    "story_viewers",
    db.metadata,
    Column("user_id", String(60), ForeignKey("users.username", ondelete="CASCADE"), primary_key=True),
    Column("story_id", String(24), ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True),
    Column("timestamp", DateTime, default=datetime.utcnow, nullable=False),
)
