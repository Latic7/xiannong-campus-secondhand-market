"""Centralized uppercase status enums for the campus market backend."""

from enum import Enum


class UppercaseStrEnum(str, Enum):
	"""String enum with uppercase member values."""


class UserStatus(UppercaseStrEnum):
	ACTIVE = "ACTIVE"
	BANNED = "BANNED"


class ProductStatus(UppercaseStrEnum):
	DRAFT = "DRAFT"
	PENDING = "PENDING"
	PUBLISHED = "PUBLISHED"
	REMOVED = "REMOVED"
	SOLD = "SOLD"


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

