#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiogram import types

import text
import keyboard as kb
from misc import dp, bot, db


@dp.message_handler(lambda message: message.text and text.MENU in message.text)
async def send_user_menu(message: types.Message):
    await bot.send_message(chat_id=message['from'].id, text=text.MENU_DESCRIBE_MESSAGE, reply_markup=kb.menu_kb)


@dp.message_handler(lambda message: message.text and text.CONTACTS in message.text)
async def send_user_menu(message: types.Message):
    await bot.send_message(chat_id=message['from'].id, text=text.CONTACTS_MESSAGE)


@dp.message_handler(lambda message: message.text and text.SHOW_CART in message.text)
async def show_cart(message: types.Message):
    cart_items = db.get_cart_items(message["from"].id)
    formatted_reply = "🛍 твій кошик зараз містить:\n\n"
    price = 0
    for item in cart_items:
        formatted_reply += f"{item['name']} \n"
        price += item['price']
    formatted_reply += f"\n💸 усього на {price} грн."
    if price == 0:
        formatted_reply = "🥺 кошик порожній"
    await bot.send_message(chat_id=message['from'].id, text=formatted_reply)


@dp.message_handler(lambda message: message.text and text.CLEAR_CART in message.text)
async def clear_cart(message: types.Message):
    db.clear_cart(message['from'].id)
    await bot.send_message(message["from"].id, text.CLEAR_CART_MESSAGE)

