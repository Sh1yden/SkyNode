__all__ = [
    "get_btns_device",
    "get_btns_exit_to_main_menu",
    "get_btns_admin_menu",
    "get_btns_start",
    "get_btns_weather_menu",
    "get_btns_exit_to_weather_menu",
    "get_btns_weather_hours",
    "get_btns_exit_to_hours_menu",
    "get_btns_settings",
]

from .k_device import get_btns_device
from .k_exit_to_main_menu import get_btns_exit_to_main_menu
from .k_admin_menu import get_btns_admin_menu
from .k_start import get_btns_start
from .k_weather_menu import get_btns_weather_menu
from .k_exit_to_weather_menu import get_btns_exit_to_weather_menu
from .k_weather_hours import get_btns_weather_hours
from .k_exit_to_hours_menu import get_btns_exit_to_hours_menu
from .k_settings import get_btns_settings
