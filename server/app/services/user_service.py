from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, Tuple

from app.models.user import User
from app.models.favorite import Favorite
from app.core.status import UserStatus


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
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        favorites_count = self.db.query(Favorite).filter(
            Favorite.user_id == user.id
        ).count()

        return {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "score": user.score,
            "status": user.status if user.status else UserStatus.ACTIVE.value,
            "isAdmin": bool(user.is_admin),
            "college": user.college,
            "contact": user.contact,
            "favorites": favorites_count,
        }

    # ========== 用户创建 ==========

    def create_or_get_user(self, openid: str) -> User:
        """创建新用户或返回已有用户"""
        user = self.get_user_by_openid(openid)

        if not user:
            default_nickname = f"WX_{openid[-6:]}"

            user = User(
                openid=openid,
                nickname=default_nickname,
                avatar="",
                score=100,
                status=UserStatus.ACTIVE.value,
                is_admin=False,
            )
            self.db.add(user)
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
        size: int = 20
    ) -> Tuple[list, int]:
        """
        获取收藏列表（分页）
        返回: (收藏列表, 总数)
        """
        offset = max(0, (page - 1) * size)
        size = max(1, size)

        favorites = self.db.query(Favorite).filter(
            Favorite.user_id == user_id
        ).order_by(Favorite.created_at.desc()).offset(offset).limit(size).all()

        total = self.db.query(Favorite).filter(Favorite.user_id == user_id).count()

        favorite_list = [
            {
                "id": fav.id,
                "productId": fav.product_id,
                "createdAt": fav.created_at.isoformat() if fav.created_at else None,
            }
            for fav in favorites
        ]

        return favorite_list, total

    # ========== 用户状态 ==========

    def update_status(self, user_id: int, status: str, reason: str = None) -> bool:
        """更新用户状态（管理员功能）"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.status = status
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
            "isAdmin": bool(user.is_admin),
        }