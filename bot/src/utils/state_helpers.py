from aiogram.fsm.context import FSMContext
from typing import Any

from common.core import get_logger

_lg = get_logger()


async def clear_state(state: FSMContext) -> None:
    """
    Clear FSM state

    Args:
        state: FSM context object
    """
    try:
        await state.clear()
        _lg.debug("State cleared successfully")
    except Exception as e:
        _lg.error(f"Error clearing state: {e}")


async def is_waiting_for_location(state: FSMContext) -> bool:
    """
    Check if bot is waiting for location input

    Args:
        state: FSM context object

    Returns:
        bool: True if waiting for location
    """
    try:
        current_state = await state.get_state()

        waiting_states = [
            "LocationState:waiting_for_city_phone",
            "LocationState:waiting_for_city_pc",
        ]

        return current_state in waiting_states

    except Exception as e:
        _lg.error(f"Error checking state: {e}")
        return False


async def get_current_state(state: FSMContext) -> str | None:
    """
    Get current FSM state name

    Args:
        state: FSM context object

    Returns:
        str | None: Current state name or None if error
    """
    try:
        current_state = await state.get_state()
        _lg.debug(f"Current state: {current_state}")
        return current_state

    except Exception as e:
        _lg.error(f"Error getting state: {e}")
        return None


async def set_state_data(state: FSMContext, data: dict[str, Any]) -> None:
    """
    Set FSM context data

    Args:
        state: FSM context object
        data: Data dictionary to set
    """
    try:
        await state.update_data(**data)
        _lg.debug(f"State data updated: {data}")

    except Exception as e:
        _lg.error(f"Error setting state data: {e}")
