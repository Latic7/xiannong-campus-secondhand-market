"""Dependency injection helpers for API routes."""
# app/api/deps/__init__.py

from app.api.deps.admin import get_current_admin

__all__ = ["get_current_admin"]