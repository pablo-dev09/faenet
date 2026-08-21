"""
FaeNet - Rotas /api/stories
===========================
Listagem, publicacao, visualizacao e remocao de stories.
"""

from flask import Blueprint, request
from flask_login import current_user, login_required

from ..services import story_service
from ..utils.responses import fail, ok
from ..utils.uploads import save_base64_data_url, save_upload

stories_bp = Blueprint("stories", __name__, url_prefix="/api/stories")


@stories_bp.route("", methods=["GET"])
@login_required
def list_stories():
    story_service.cleanup_expired()
    return ok(story_service.list_active(current_user))


@stories_bp.route("", methods=["POST"])
@login_required
def create_story():
    image_url = None
    caption = None

    # Suporta tanto JSON (data_url) quanto multipart.
    if request.is_json:
        data = request.get_json(silent=True) or {}
        image_url = data.get("image_url")
        caption = data.get("caption")
        data_url = data.get("image_data_url")
        if not image_url and data_url:
            image_url = save_base64_data_url(data_url, "story")
    else:
        if "file" in request.files:
            image_url = save_upload(request.files["file"], "story")
        data_url = request.form.get("image_data_url")
        if not image_url and data_url:
            image_url = save_base64_data_url(data_url, "story")
        caption = request.form.get("caption")

    if not image_url:
        return fail("Imagem obrigatoria.", 400)

    try:
        story = story_service.create_story(
            author=current_user,
            image_url=image_url,
            caption=caption,
        )
    except story_service.StoryError as exc:
        return fail(exc.message, exc.status)
    return ok(story.to_dict(current_user=current_user.username), 201)


@stories_bp.route("/<story_id>", methods=["DELETE"])
@login_required
def delete_story(story_id: str):
    try:
        story_service.delete_story(viewer=current_user, story_id=story_id)
    except story_service.StoryError as exc:
        return fail(exc.message, exc.status)
    return ok({"deleted": True})


@stories_bp.route("/<story_id>/view", methods=["POST"])
@login_required
def view_story(story_id: str):
    story_service.mark_viewed(viewer=current_user, story_id=story_id)
    return ok({"ok": True})
