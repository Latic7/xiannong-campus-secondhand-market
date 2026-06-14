"""Dependency injection helpers for API routes."""
from app.api.deps.admin import get_current_admin
from app.api.deps.auth import CurrentActor, get_current_actor

__all__ = ["CurrentActor", "get_current_actor", "get_current_admin"]
