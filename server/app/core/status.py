"""Centralized uppercase status enums for the campus market backend."""

from enum import Enum


class UppercaseStrEnum(str, Enum):
	"""String enum with uppercase member values."""


class UserStatus(UppercaseStrEnum):
	ACTIVE = "active"
	BANNED = "banned"


class ProductStatus(UppercaseStrEnum):
	DRAFT = "draft"
	PENDING = "pending"
	PUBLISHED = "published"
	REMOVED = "removed"
	SOLD = "sold"


class OrderStatus(UppercaseStrEnum):
	CREATED = "CREATED"
	RESERVED = "RESERVED"
	CONFIRMED = "CONFIRMED"
	COMPLETED = "COMPLETED"
	CANCELLED = "CANCELLED"


class ReportStatus(UppercaseStrEnum):
	OPEN = "OPEN"
	REJECTED = "REJECTED"
	HANDLED = "HANDLED"


class ReportTargetType(UppercaseStrEnum):
	PRODUCT = "PRODUCT"
	USER = "USER"
	ORDER = "ORDER"

