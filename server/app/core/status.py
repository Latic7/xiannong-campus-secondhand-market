from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


class ProductStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    REMOVED = "REMOVED"
    SOLD = "SOLD"


class OrderStatus(StrEnum):
    CREATED = "CREATED"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReportStatus(StrEnum):
    OPEN = "OPEN"
    REJECTED = "REJECTED"
    HANDLED = "HANDLED"


class ReportTargetType(StrEnum):
    PRODUCT = "PRODUCT"
    USER = "USER"
    ORDER = "ORDER"
