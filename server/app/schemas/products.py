from typing import Literal

from pydantic import BaseModel, Field


ProductStatusValue = Literal["draft", "pending", "published", "removed", "sold"]
ProductUpdateStatusValue = Literal["pending", "published", "removed"]


class ProductCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    price: float = Field(ge=0)
    categoryId: int
    description: str | None = None
    images: list[str] = Field(default_factory=list)


class ProductUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=128)
    price: float | None = Field(default=None, ge=0)
    categoryId: int | None = None
    description: str | None = None
    status: ProductUpdateStatusValue | None = None
    images: list[str] | None = None


class Product(BaseModel):
    id: int
    ownerId: int | None = None
    title: str
    description: str | None = None
    price: float
    categoryId: int | None = None
    status: ProductStatusValue
    images: list[str] = Field(default_factory=list)
    createdAt: str | None = None
    updatedAt: str | None = None
    favoriteCount: int | None = 0
    viewCount: int | None = 0


class PageMeta(BaseModel):
    page: int
    size: int
    total: int


class ProductFilters(BaseModel):
    keyword: str | None = None
    sort: str | None = None
    categoryId: int | None = None


class ProductListPayload(BaseModel):
    list: list[Product]
    page: PageMeta
    filters: ProductFilters | None = None
