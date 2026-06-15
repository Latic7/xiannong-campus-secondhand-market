from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import api_ok
from app.crud.category import list_categories

router = APIRouter(tags=["Category"])


@router.get("/api/categories")
def get_categories(db: Session = Depends(get_db)) -> dict:
    """Get all product categories, sorted by sort_order then id."""
    return api_ok(list_categories(db))
