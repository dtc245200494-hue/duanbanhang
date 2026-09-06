from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import hash_password, require_roles
from app.config import ROLES
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/api/users", tags=["users"])
admin_only = Depends(require_roles("admin"))


@router.get("", response_model=List[UserOut], dependencies=[admin_only])
def list_users(db: Session = Depends(get_db), keyword: str = ""):
    q = db.query(User)
    if keyword:
        q = q.filter(User.username.ilike(f"%{keyword}%") | User.full_name.ilike(f"%{keyword}%"))
    return q.order_by(User.id).all()


@router.post("", response_model=UserOut, status_code=201, dependencies=[admin_only])
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    if body.role not in ROLES:
        raise HTTPException(status_code=400, detail=f"Vai trò phải thuộc {ROLES}")
    if db.query(User).filter(User.username == body.username.strip()).first():
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    user = User(
        username=body.username.strip(),
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut, dependencies=[admin_only])
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    if body.role is not None:
        if body.role not in ROLES:
            raise HTTPException(status_code=400, detail=f"Vai trò phải thuộc {ROLES}")
        user.role = body.role
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.status is not None:
        user.status = body.status
    if body.password:
        user.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", dependencies=[admin_only])
def delete_user(user_id: int, db: Session = Depends(get_db), current: User = Depends(require_roles("admin"))):
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính mình")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    user.status = "disabled"
    db.commit()
    return {"detail": "Đã khóa tài khoản"}
