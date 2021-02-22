#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import Time, ME
import text
import keyboard as kb
from misc import dp, bot, db, wfp
import datetime


class OrderStates(StatesGroup):
    storage = MemoryStorage()
    get_phone_number = State()
    grind_coffee_pack = State()
    type_of_grind = State()
    set_delivery_spot = State()
    get_address = State()
    get_arriving_time = State()


async def alert_admins(message):
    admins = db.get_admins()
    await bot.send_message(ME, message)
    # for admin in admins:
    #     await bot.send_message(admin[0], message)


async def organize_info(user_id, data):
    cart_items = db.get_cart_items(user_id)
    try:
        grind_type = f"\nкаву змолоти під {data['grind_type']}\n"
    except:
        grind_type = ""
    try:
        delivery_address = f"🚕 доставка на таксі: {data['address']}"
    except:
        delivery_address = "📍 забере сам через"
    try:
        arriving_time = f"{data['arriving_time']} хв"
    except:
        arriving_time = ""
    user_number = db.get_user_number(user_id)
    ret = wfp.create_ticket(user_id, cart_items, delivery_address)
    formatted_reply = f"🛍 нове замовлення від: {user_number}\n📲 id: {user_id}\n{delivery_address} {arriving_time}\n" \
                      f"📩 номер замовлення: {ret['order_reference']}\n\n"
    price = 0
    for item in cart_items:
        formatted_reply += f"{item['name']} \n"
        price += item['price']
    formatted_reply += grind_type
    formatted_reply += f"\n💸 усього на {price} грн."
    await bot.send_message(user_id, ret["link"])
    await bot.send_message(user_id, text.WAITING_FOR_PAY, reply_markup=kb.main_kb)
    await alert_admins(message=formatted_reply)


@dp.message_handler(lambda message: message.text and text.BACK in message.text, state="*")
async def back_button_pressed(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message["from"].id, text.WELCOME_MESSAGE, reply_markup=kb.main_kb)


@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=OrderStates.get_phone_number)
async def update_phone_number(message: types.Message, state: FSMContext):
    db.update_phone_number(message["from"].id, message.contact['phone_number'])
    data = await state.get_data()
    await organize_info(user_id=message["from"].id, data=data)
    await state.finish()


@dp.message_handler(lambda message: message.text and text.CREATE_ORDER in message.text)
async def create_order(message: types.Message):
    cart_items = db.get_cart_items(message["from"].id)

    def include_coffee_pack() -> bool:
        for item in cart_items:
            if item["type"] == "coffee":
                return True
        return False

    t = datetime.datetime.utcnow().hour + Time.UTC_DIFF
    if t > Time.CAFE_CLOSES - 1 or t < Time.CAFE_OPENS:
        await bot.send_message(message["from"].id, text.CAFE_IS_CLOSED, reply_markup=kb.main_kb)
        return

    if len(cart_items) < 1:
        await bot.send_message(message["from"].id, text.CART_CANNOT_BE_EMPTY, reply_markup=kb.main_kb)
        return
    if include_coffee_pack():
        await OrderStates.grind_coffee_pack.set()
        await bot.send_message(message["from"].id, text=text.COFFEE_PACK_IS_IN_MENU, reply_markup=kb.choise_kb)
    else:
        await OrderStates.set_delivery_spot.set()
        await bot.send_message(message["from"].id, text.SET_DELIVERY_SPOT, reply_markup=kb.delivery_spot_kb)


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderStates.grind_coffee_pack)
async def set_coffee_pack_grind(message: types.Message, state: FSMContext):
    if message.text == text.YES:
        await state.update_data(to_grind=text.YES)
        await OrderStates.type_of_grind.set()
        await bot.send_message(message["from"].id, text.CHOOSE_GRIND_TYPE, reply_markup=kb.grind_types_kb)
    elif message.text == text.NO:
        await OrderStates.set_delivery_spot.set()
        await state.update_data(to_grind=text.NO)
        await bot.send_message(message["from"].id, text.SET_DELIVERY_SPOT, reply_markup=kb.delivery_spot_kb)
    else:
        return


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderStates.type_of_grind)
@dp.message_handler(lambda message: message.text and text.YES in message.text)
async def set_type_of_grind(message: types.Message, state: FSMContext):
    if message.text in text.GRIND_TYPES:
        await state.update_data(grind_type=message.text)
        await OrderStates.set_delivery_spot.set()
        await bot.send_message(message["from"].id, text.SET_DELIVERY_SPOT, reply_markup=kb.delivery_spot_kb)
    else:
        await bot.send_message(message["from"].id, text.CHOOSE_GRIND_TYPE, reply_markup=kb.grind_types_kb)
        return


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderStates.set_delivery_spot)
@dp.message_handler(lambda message: message.text and text.DELIVERY_OLC or text.DELIVERY_TAXI in message.text)
async def set_delivery_spot(message: types.Message, state: FSMContext):
    if message.text == text.DELIVERY_OLC:
        await state.update_data(delivery=text.DELIVERY_OLC)
        await OrderStates.get_arriving_time.set()
        await bot.send_message(message["from"].id, text.TYPE_ARRIVING_TIME)
    elif message.text == text.DELIVERY_TAXI:
        await OrderStates.get_address.set()
        await bot.send_message(message["from"].id, text.TYPE_DELIVERY_ADDRESS)


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderStates.get_address)
async def get_address(message: types.Message, state: FSMContext):
    if len(message.text) > 4:
        await state.update_data(address=message.text.lower())
    else:
        await bot.send_message(message["from"].id, text.TYPE_DELIVERY_ADDRESS)
        return
    # await bot.send_message(message["from"].id, await state.get_data())
    if db.get_user_number(message["from"].id) == 0:
        await OrderStates.get_phone_number.set()
        await bot.send_message(chat_id=message["from"].id, text=text.SHARE_YOUR_NUMBER, reply_markup=kb.share_phone_kb)
    else:
        data = await state.get_data()
        await organize_info(user_id=message["from"].id, data=data)
        await state.finish()


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=OrderStates.get_arriving_time)
async def get_time(message: types.Message, state: FSMContext):
    def process_time(item: str) -> int:
        if item.isdigit():
            return int(item)
        else:
            if item[0:2].isdigit():
                return int(item[0:2])
            elif item[0:1].isdigit():
                return int(item[0:1])
            else:
                return -1

    time_data = message.text.split(" ")[0]
    time = 0
    if time_data.isdigit():
        time = int(time_data)
    else:
        time = process_time(message.text)
    if time != 0:
        await state.update_data(arriving_time=time)
    else:
        await bot.send_message(message["from"].id, text.TYPE_ARRIVING_TIME)
        return
    if db.get_user_number(message["from"].id) == 0:
        await OrderStates.get_phone_number.set()
        await bot.send_message(chat_id=message["from"].id, text=text.SHARE_YOUR_NUMBER, reply_markup=kb.share_phone_kb)
    else:
        data = await state.get_data()
        await organize_info(user_id=message["from"].id, data=data)
        await state.finish()
