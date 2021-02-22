from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


class OrderStates(StatesGroup):
    storage = MemoryStorage()
    grind_coffee_pack = State()
    type_of_grind = State()
    set_delivery_spot = State()
    set_delivery_time = State()
