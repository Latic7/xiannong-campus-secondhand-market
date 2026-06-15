from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


def list_categories(db: Session) -> list[dict]:
    rows = db.execute(
        select(Category).order_by(Category.sort_order, Category.id)
    ).scalars().all()
    return [
        {"id": cat.id, "name": cat.name, "parentId": cat.parent_id, "sortOrder": cat.sort_order}
        for cat in rows
    ]
