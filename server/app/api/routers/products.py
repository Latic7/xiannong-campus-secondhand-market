from fastapi import APIRouter, File, UploadFile, Request

from app.core.exceptions import ResourceNotFoundError
from app.core.response import api_ok
from app.schemas.common import ProductCreateRequest, ProductUpdateRequest
from app.services import product_service
from app.utils import file_handler

router = APIRouter(prefix="/api/products", tags=["Product"])


@router.get("")
def list_products(
    page: int = 1,
    size: int = 20,
    keyword: str | None = None,
    sort: str | None = None,
    categoryId: int | None = None,
) -> dict:
    return api_ok(product_service.list_products(page, size, keyword, sort, categoryId))


@router.post("")
def create_product(payload: ProductCreateRequest) -> dict:
    return api_ok(product_service.create_product(payload))


@router.get("/{product_id}")
def get_product(product_id: int) -> dict:
    product = product_service.get_product(product_id)
    if product is None:
        raise ResourceNotFoundError("product not found", {"productId": product_id})
    return api_ok(product)


@router.put("/{product_id}")
def update_product(product_id: int, payload: ProductUpdateRequest) -> dict:
    product_service.update_product(product_id, payload)
    return api_ok({"updated": True, "productId": product_id})


@router.delete("/{product_id}")
def delete_product(product_id: int) -> dict:
    # 先清理图片引用，再移除商品
    product_service.cleanup_product_images(product_id)
    return api_ok(product_service.remove_product(product_id))


@router.post("/{product_id}/images")
async def upload_product_image(product_id: int, file: UploadFile = File(...), request: Request = None) -> dict:
    # 1. 校验文件扩展名
    ext = file_handler.validate_image(file)

    # 2. 读取文件内容并校验大小
    content = await file_handler.read_and_check_size(file)

    # 3. 生成 UUID 文件名
    filename = file_handler.generate_filename(ext)

    # 4. 保存到本地磁盘
    file_path = file_handler.save_file(content, filename)

    # 5. 生成完整可访问 URL（含 scheme + host）
    media_url = file_handler.get_media_url(filename)
    base_url = str(request.base_url).rstrip("/") if request else "http://localhost:8000"
    full_url = f"{base_url}{media_url}"

    # 6. 记录到数据库
    image = product_service.upload_product_image(
        product_id, full_url, str(file_path)
    )

    return api_ok({
        "productId": product_id,
        "imageId": image["id"],
        "url": image["url"],
    })


@router.delete("/{product_id}/images/{image_id}")
def delete_product_image(product_id: int, image_id: int) -> dict:
    return api_ok(product_service.delete_product_image(product_id, image_id))
