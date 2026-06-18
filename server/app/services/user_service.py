from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.models.user import User
from app.models.favorite import Favorite
from app.core.status import UserStatus, ProductStatus


class UserService:
    """用户服务层，处理所有用户相关的业务逻辑"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== 用户查询 ==========
    
    def get_user_by_openid(self, openid: str) -> Optional[User]:
        """根据 openid 获取用户"""
        return self.db.query(User).filter(User.openid == openid).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据用户 ID 获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户资料（包含统计信息）"""
        from app.models.product import Product

        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # 统计收藏数量
        favorites_count = self.db.query(Favorite).filter(
            Favorite.user_id == user.id
        ).count()

        # 统计已发布和已售出商品数量
        # 注：published_count 统计用户所有商品（含 PENDING/PUBLISHED/REMOVED/SOLD），
        #     与"我的发布"列表的口径一致。sold_count 仅统计 SOLD 终态。
        published_count = self.db.query(Product).filter(
            Product.owner_id == user.id,
        ).count()
        sold_count = self.db.query(Product).filter(
            Product.owner_id == user.id,
            Product.status == ProductStatus.SOLD.value,
        ).count()
        
        return {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "score": user.score,
            "status": user.status if user.status else "active",  # 直接返回数据库值（小写）
            "isAdmin": user.is_admin,  # 改为 isAdmin（驼峰命名，与 OpenAPI 一致）
            "college": user.college,
            "contact": user.contact,
            "favorites": favorites_count,
            "publishedCount": published_count,
            "soldCount": sold_count,
        }
    
    # ========== 用户创建 ==========
    
    def create_or_get_user(self, openid: str, is_admin: bool = False) -> User:
        """创建新用户或返回已有用户"""
        user = self.get_user_by_openid(openid)
        
        if not user:
            # 生成默认昵称（使用 openid 后6位）
            default_nickname = f"WX_{openid[-6:]}"
            
            user = User(
                openid=openid,
                nickname=default_nickname,
                avatar="",
                score=100,
                status="active",  # 数据库存储小写
                is_admin=is_admin,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif is_admin and not user.is_admin:
            # 如果提供了管理员权限且用户还不是管理员，升级
            user.is_admin = True
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    # ========== 用户更新 ==========
    
    def update_profile(
        self, 
        user_id: int, 
        nickname: Optional[str] = None,
        avatar: Optional[str] = None,
        college: Optional[str] = None,
        contact: Optional[str] = None
    ) -> Tuple[bool, Optional[User], Dict[str, Any]]:
        """
        更新用户资料
        返回: (是否成功, 更新后的用户对象, 更新的字段)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, None, {}
        
        updated_fields = {}
        
        if nickname is not None:
            user.nickname = nickname
            updated_fields["nickname"] = nickname
        if avatar is not None:
            user.avatar = avatar
            updated_fields["avatar"] = avatar
        if college is not None:
            user.college = college
            updated_fields["college"] = college
        if contact is not None:
            user.contact = contact
            updated_fields["contact"] = contact
        
        if updated_fields:
            self.db.commit()
            self.db.refresh(user)
        
        return True, user, updated_fields
    
    # ========== 收藏管理 ==========
    
    def is_favorited(self, user_id: int, product_id: int) -> bool:
        """检查用户是否已收藏某个商品"""
        return self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        ).first() is not None
    
    def add_favorite(self, user_id: int, product_id: int) -> bool:
        """
        添加收藏
        返回: 是否新增成功（如果已存在则返回 False）
        """
        if self.is_favorited(user_id, product_id):
            return False
        
        favorite = Favorite(
            user_id=user_id,
            product_id=product_id
        )
        self.db.add(favorite)
        self.db.commit()
        return True
    
    def remove_favorite(self, user_id: int, product_id: int) -> bool:
        """
        取消收藏
        返回: 是否删除成功
        """
        favorite = self.db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        ).first()
        
        if not favorite:
            return False
        
        self.db.delete(favorite)
        self.db.commit()
        return True
    
    def get_favorites(
        self, 
        user_id: int, 
        page: int = 1, 
        size: int = 20,
        keyword: str | None = None,
        sort: str | None = None,
        category_id: int | None = None,
    ) -> Tuple[list, int]:
        """
        获取收藏列表（分页 + 筛选），返回完整商品信息，对齐 OpenAPI ProductListPayload。
        """
        from app.models.product import Product
        from app.models.product_image import ProductImage
        from decimal import Decimal

        offset = max(0, (page - 1) * size)
        size = max(1, size)

        # JOIN products 查完整商品信息
        query = (
            self.db.query(Favorite, Product)
            .join(Product, Favorite.product_id == Product.id, isouter=True)
            .filter(Favorite.user_id == user_id)
        )

        # 筛选
        if keyword:
            kw = f"%{keyword}%"
            query = query.filter(
                Product.title.ilike(kw) | Product.description.ilike(kw)
            )
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)

        # 统计总数
        total = query.count()

        # 排序
        if sort == "price_asc":
            query = query.order_by(Product.price.asc())
        elif sort == "price_desc":
            query = query.order_by(Product.price.desc())
        else:
            query = query.order_by(Favorite.created_at.desc())

        rows = query.offset(offset).limit(size).all()

        favorite_list = []
        for fav, prod in rows:
            if prod is None:
                continue
            images = [
                row[0] for row in
                self.db.query(ProductImage.url)
                .filter(ProductImage.product_id == prod.id)
                .all()
            ]
            # 查卖家信息
            seller = {"id": 0, "nickname": "未知用户", "avatar": "", "reputation": 0}
            if prod.owner_id:
                owner = self.db.get(User, prod.owner_id)
                if owner:
                    seller = {
                        "id": owner.id,
                        "nickname": owner.nickname or "未知用户",
                        "avatar": owner.avatar or "",
                        "reputation": owner.score if owner.score is not None else 100,
                    }
            favorite_list.append({
                "id": prod.id,
                "ownerId": prod.owner_id,
                "title": prod.title,
                "description": prod.description or "",
                "price": float(prod.price) if isinstance(prod.price, Decimal) else float(prod.price or 0),
                "categoryId": prod.category_id,
                "status": prod.status,
                "images": images,
                "createdAt": prod.created_at.isoformat() if prod.created_at else "",
                "updatedAt": prod.updated_at.isoformat() if prod.updated_at else "",
                "favoriteCount": prod.favorite_count or 0,
                "viewCount": prod.view_count or 0,
                "seller": seller,
            })

        return favorite_list, total
    
    # ========== 用户状态 ==========
    
    def update_status(self, user_id: int, status: str, reason: str = None) -> bool:
        """更新用户状态（管理员功能）"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = status
        # 如果有 reason 字段，可以记录封禁原因
        # user.status_reason = reason
        
        self.db.commit()
        return True
    
    def get_simple_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户简要信息（用于 token 生成）"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": user.id,
            "openid": user.openid,
            "nickname": user.nickname,
            "isAdmin": user.is_admin,  # 改为 isAdmin
        }