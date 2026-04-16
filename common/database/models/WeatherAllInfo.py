from typing import Optional

from sqlalchemy import Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from common.database.core.database import Base


class WeatherAllInfo(Base):
    """
    ## Table name: \n
    weather_all_info \n
    """

    __tablename__ = "weather_all_info"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,  # NOT NULL
    )

    weather_id: Mapped[str] = mapped_column(String, nullable=False)

    weather_now_msg: Mapped[Optional[str]] = mapped_column(String)
    weather_hours_msg: Mapped[Optional[bytes]] = mapped_column(String)
    weather_day_night_msg: Mapped[Optional[str]] = mapped_column(LargeBinary)
    weather_5d_msg: Mapped[Optional[str]] = mapped_column(String)
    weather_rain_msg: Mapped[Optional[str]] = mapped_column(String)
    weather_wind_pressure_msg: Mapped[Optional[str]] = mapped_column(String)

    def __repr__(self):
        return f"<Weather(weather_id={self.weather_id}, weather_now_msg='{self.weather_now_msg})'>"
