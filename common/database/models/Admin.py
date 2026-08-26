from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from common.database.core.database import Base


class Admin(Base):
    """"""

    __tablename__ = "admins"
    __table_args__ = {"extend_existing": True}

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )

    def __repr__(self):
        return f"<Admin(user_id={self.user_id})>"
