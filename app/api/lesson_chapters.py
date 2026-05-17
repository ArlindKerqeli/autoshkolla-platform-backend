from flask import request, g, jsonify
from datetime import datetime, time
from sqlalchemy import func

from app.api import api_bp
from app.models.lesson_chapter_model import LessonChapter
from app.models.category_model import Category
from app.schemas.lesson_chapters import CreateLessonChapterSchema, UpdateLessonChapterSchema
from app.utils.validation import parse_body, ValidationError
from app.utils.pagination import paginate_query
from app.utils.db import db
from app.middleware.error_handler import NotFound, Forbidden


def _require_admin():
    if g.current_user.get('role') not in ('administrator', 'super_admin'):
        raise Forbidden('Administrator access required')


def _parse_time(time_str: str) -> time:
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        raise ValidationError(f'Invalid time format: {time_str}')


@api_bp.get('/lesson-chapters')
def list_lesson_chapters():
    """List lesson chapters, optionally filtered by categoryId and chapterType."""
    _require_admin()

    category_id = request.args.get('categoryId')
    chapter_type = request.args.get('chapterType')

    query = LessonChapter.query.filter_by(tenant_id=g.tenant_id)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if chapter_type:
        if chapter_type not in ('theory', 'practical'):
            raise ValidationError('chapterType must be "theory" or "practical"')
        query = query.filter_by(chapter_type=chapter_type)

    query = query.order_by(
        LessonChapter.category_id,
        LessonChapter.chapter_type,
        LessonChapter.session_number,
    )

    result = paginate_query(query)
    result['data'] = [c.to_dict() for c in result['data']]
    return result


@api_bp.get('/lesson-chapters/<chapter_id>')
def get_lesson_chapter(chapter_id):
    """Get a specific lesson chapter."""
    _require_admin()

    chapter = LessonChapter.query.filter_by(
        id=chapter_id, tenant_id=g.tenant_id
    ).first()
    if not chapter:
        raise NotFound('Lesson chapter not found')

    return jsonify(chapter.to_dict())


@api_bp.post('/lesson-chapters')
def create_lesson_chapter():
    """Create a new lesson chapter with auto-assigned session_number."""
    _require_admin()
    payload = parse_body(CreateLessonChapterSchema, request.get_json(silent=True) or {})

    if payload.chapterType not in ('theory', 'practical'):
        raise ValidationError('chapterType must be "theory" or "practical"')

    category = Category.query.filter_by(
        id=payload.categoryId, tenant_id=g.tenant_id
    ).first()
    if not category:
        raise NotFound('Category not found')

    max_num = db.session.query(func.max(LessonChapter.session_number)).filter_by(
        tenant_id=g.tenant_id,
        category_id=payload.categoryId,
        chapter_type=payload.chapterType,
    ).scalar() or 0

    chapter = LessonChapter(
        tenant_id=g.tenant_id,
        category_id=payload.categoryId,
        chapter_type=payload.chapterType,
        session_number=max_num + 1,
        chapter_topics=payload.chapterTopics,
        time_from=_parse_time(payload.timeFrom) if payload.timeFrom else None,
        time_to=_parse_time(payload.timeTo) if payload.timeTo else None,
        hours_count=payload.hoursCount or 2,
        is_active=payload.isActive if payload.isActive is not None else True,
    )
    db.session.add(chapter)
    db.session.commit()

    return jsonify(chapter.to_dict()), 201


@api_bp.put('/lesson-chapters/<chapter_id>')
def update_lesson_chapter(chapter_id):
    """Update a lesson chapter."""
    _require_admin()

    chapter = LessonChapter.query.filter_by(
        id=chapter_id, tenant_id=g.tenant_id
    ).first()
    if not chapter:
        raise NotFound('Lesson chapter not found')

    payload = parse_body(UpdateLessonChapterSchema, request.get_json(silent=True) or {})

    if payload.chapterTopics is not None:
        chapter.chapter_topics = payload.chapterTopics
    if payload.timeFrom is not None:
        chapter.time_from = _parse_time(payload.timeFrom)
    if payload.timeTo is not None:
        chapter.time_to = _parse_time(payload.timeTo)
    if payload.hoursCount is not None:
        chapter.hours_count = payload.hoursCount
    if payload.isActive is not None:
        chapter.is_active = payload.isActive

    db.session.commit()
    return jsonify(chapter.to_dict())


@api_bp.delete('/lesson-chapters/<chapter_id>')
def delete_lesson_chapter(chapter_id):
    """Delete a lesson chapter and re-number remaining chapters."""
    _require_admin()

    chapter = LessonChapter.query.filter_by(
        id=chapter_id, tenant_id=g.tenant_id
    ).first()
    if not chapter:
        raise NotFound('Lesson chapter not found')

    cat_id = chapter.category_id
    ch_type = chapter.chapter_type
    deleted_num = chapter.session_number

    db.session.delete(chapter)
    db.session.flush()

    remaining = LessonChapter.query.filter(
        LessonChapter.tenant_id == g.tenant_id,
        LessonChapter.category_id == cat_id,
        LessonChapter.chapter_type == ch_type,
        LessonChapter.session_number > deleted_num,
    ).order_by(LessonChapter.session_number).all()

    offset = 10000
    for ch in remaining:
        ch.session_number += offset
    db.session.flush()

    for ch in remaining:
        ch.session_number = ch.session_number - offset - 1

    db.session.commit()
    return '', 204
