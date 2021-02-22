#!/usr/bin/env python
# -*- coding: utf-8 -*-

from misc import dp, bot, db, wfp, menu
from aiogram import types
import text
import keyboard as kb
import config

ENTERED_EDIT_MODE = "ENTERED_EDIT_MODE"


@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message):
    print("START")
    db.user_init(message["from"].id)
    db.get_admins()
    await bot.send_message(chat_id=message["from"].id, text=text.WELCOME_MESSAGE, reply_markup=kb.main_kb)
    await bot.send_message(chat_id=config.ME, text=f"Started:{message['from']}")


@dp.message_handler(commands=['add_admin'])
async def add_admin(message: types.Message):
    db.user_init(message['from'].id, 42)


@dp.message_handler(commands=['remove_admin'])
async def remove_admin():
    # await admin.remove_admin()
    pass


@dp.message_handler(commands=['admin'])
async def edit_coffee_menu(message: types.Message):
    if db.is_admin(message["from"].id):
        await bot.send_message(message["from"].id, ENTERED_EDIT_MODE, reply_markup=kb.edit_menu_kb)


@dp.message_handler(commands=['check'])
async def check_ticket(message: types.Message):
    order_reference = message.text[7:]
    if order_reference:
        ret = wfp.check_ticket_status(order_reference)
        # TODO change me to all admins
        await bot.send_message(config.ME, ret)
    else:
        await bot.send_message(config.ME, '⚠️ Input order id')


@dp.message_handler(commands=['show_info'])
async def show_info(message: types.Message):
    menu_type = message.text.split(" ")[1]
    menu_view = menu.format_view_for_admin(menu_type)
    await bot.send_message(config.ME, menu_view)


@dp.message_handler(commands=['change_price'])
async def change_price(message: types.Message):
    # input: /change_price <menu_type> <id of item to be changed> <new price>
    data = message.text.split(" ")
    if len(data) > 2:
        menu_type = data[1]
        item_id = data[2]
        new_price = data[3]
        if db.change_price(menu_type, item_id, new_price):
            db.get_menu(menu)
            await bot.send_message(message["from"].id, "The price has been successfully changed.")
            return
    await bot.send_message(message["from"].id, "Wrong format.")

