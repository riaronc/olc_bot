#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import keyboard as kb
import text
import config
from misc import dp, bot, db, wfp, menu


class EditMenuStates(StatesGroup):
    storage = MemoryStorage()
    get_id = State()
    get_name = State()
    get_type = State()
    get_price = State()


@dp.message_handler(lambda message: message.text and text.BACK in message.text, state='*')
async def exit_edit_mode(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message["from"].id, "Exited edit mode", reply_markup=kb.main_kb)


@dp.message_handler(lambda message: message.text and text.SHOW_ALL in message.text)
async def show_all_items(message: types.Message):
    menu_view = menu.format_view_for_admin(menu_type="coffee")
    await bot.send_message(message["from"].id, menu_view)


@dp.message_handler(lambda message: message.text and text.DELETE in message.text)
async def item_delete_mode(message: types.Message):
    await EditMenuStates.get_id.set()
    menu_view = menu.format_view_for_admin(menu_type="coffee")
    await bot.send_message(message["from"].id, menu_view)
    await bot.send_message(message["from"].id, "обери номер позиції, що потрібно видалити")


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=EditMenuStates.get_id)
async def set_name(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        item_id = int(message.text.lower())
        db.delete_item(table='coffee', item_id=item_id)
        db.get_menu(menu)
        await state.finish()
        await bot.send_message(message["from"].id, "✅ видалено", reply_markup=kb.edit_menu_kb)
    else:
        await bot.send_message(message["from"].id, "⚠️ введи, будь-ласка, лише номер позиції, що вказано перед назвою")
        return


@dp.message_handler(lambda message: message.text and text.NEW in message.text)
async def set_add_state(message: types.Message):
    await bot.send_message(message["from"].id, "Enter a name")
    await EditMenuStates.get_name.set()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=EditMenuStates.get_name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    await EditMenuStates.get_type.set()
    await bot.send_message(message["from"].id, "Choose pack type", reply_markup=kb.coffee_type_kb)


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=EditMenuStates.get_type)
async def set_price(message: types.Message, state: FSMContext):
    if message.text == text.FILTER:
        data = ', фільтр обсмажка'
        img_link = config.FILTER_LINK
    elif message.text == text.ESPRESSO:
        data = ', еспресо обсмажка'
        img_link = config.ESPRESSO_LINK
    else:
        await bot.send_message(message["from"].id, "Choose a type only from a kb's buttons")
        return
    await state.update_data(type=data, img_link=img_link)
    await EditMenuStates.get_price.set()
    await bot.send_message(message["from"].id, "Enter a price")


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=EditMenuStates.get_price)
async def add_an_item(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(price=message.text)
        data = await state.get_data()
        name = data["name"] + data["type"]
        db.add_new_item(table="coffee", name=name, price=int(data["price"]), img_link=data["img_link"])
        db.get_menu(menu)
        await bot.send_message(message["from"].id, data, reply_markup=kb.edit_menu_kb)
        await state.finish()
    else:
        await bot.send_message(message["from"].id, "Enter only numbers")
        return
