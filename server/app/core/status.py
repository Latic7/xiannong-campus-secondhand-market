from enum import StrEnum


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
