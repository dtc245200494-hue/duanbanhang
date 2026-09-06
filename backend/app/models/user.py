from sqlalchemy import Column, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False, default="")
    role = Column(String(20), nullable=False, default="owner", index=True)
    status = Column(String(20), nullable=False, default="active")

    @property
    def role_label(self) -> str:
        return {
            "admin": "Quản trị viên",
            "owner": "Chủ cửa hàng",
        }.get(self.role, self.role)
