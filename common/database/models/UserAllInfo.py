from typing import Optional

from sqlalchemy import Integer, BigInteger, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from common.database.core.database import Base


class UserAllInfo(Base):
    """
    ## Table name: \n
    user_all_info \n
    ## All Columns: \n
    #### NOT NULL Columns:
    [ id ][ user_id ][ is_bot ][ first_name ] \n
    #### System column: \n
    [ id ] \n
    #### User data: \n
    [ user_id ][ is_bot ][ is_premium ][ language_code ][ supports_inline_queries ] \n
    \n
    #### User names: \n
    [ username ][ first_name ][ last_name ] \n
    #### Location data: \n
    [ city ][ latitude ][ longitude ]
    """

    __tablename__ = "user_all_info"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,  # NOT NULL
    )

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_premium: Mapped[Optional[bool]] = mapped_column(Boolean)
    language_code: Mapped[Optional[str]] = mapped_column(String)
    supports_inline_queries: Mapped[Optional[bool]] = mapped_column(Boolean)

    username: Mapped[Optional[str]] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String)

    city: Mapped[Optional[str]] = mapped_column(String)
    latitude: Mapped[Optional[str]] = mapped_column(String)
    longitude: Mapped[Optional[str]] = mapped_column(String)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, first_name='{self.first_name})'>"
