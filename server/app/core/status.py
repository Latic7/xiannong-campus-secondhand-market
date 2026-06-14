from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    BANNED = "banned"


class ProductStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    REMOVED = "removed"
    SOLD = "sold"


class OrderStatus(StrEnum):
    CREATED = "created"
    RESERVED = "reserved"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReportStatus(StrEnum):
    OPEN = "open"
    REJECTED = "rejected"
    HANDLED = "handled"


class ReportTargetType(StrEnum):
    PRODUCT = "product"
    USER = "user"
    ORDER = "order"
