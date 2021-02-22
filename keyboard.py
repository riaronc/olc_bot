#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aiogram.types import  \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import text

back_button = KeyboardButton(text=text.BACK)

menu_button = KeyboardButton(text=text.MENU)
contacts_button = KeyboardButton(text=text.CONTACTS)
show_cart_button = KeyboardButton(text=text.SHOW_CART)
clear_cart_button = KeyboardButton(text=text.CLEAR_CART)
order_button = KeyboardButton(text=text.CREATE_ORDER)
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
main_kb.row(menu_button, contacts_button)
main_kb.row(show_cart_button, clear_cart_button)
main_kb.row(order_button)


drinks_button = InlineKeyboardButton(text=text.DRINKS, switch_inline_query_current_chat='drinks')
coffee_button = InlineKeyboardButton(text=text.COFFEE, switch_inline_query_current_chat='coffee')
desserts_button = InlineKeyboardButton(text=text.DESSERTS, switch_inline_query_current_chat='desserts')
food_button = InlineKeyboardButton(text=text.FOOD, switch_inline_query_current_chat='food')
menu_kb = InlineKeyboardMarkup(row_width=2)
menu_kb.add(drinks_button, coffee_button)
menu_kb.add(food_button, desserts_button)


add_to_cart_button = InlineKeyboardButton(text=text.ADD_TO_CART, callback_data='order')
tools_menu = InlineKeyboardMarkup(row_width=2)
tools_menu.add(add_to_cart_button)


yes_button = KeyboardButton(text=text.YES)
no_button = KeyboardButton(text=text.NO)
choise_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
choise_kb.row(yes_button, no_button)
choise_kb.row(back_button)


olc_button = KeyboardButton(text=text.DELIVERY_OLC)
taxi_button = KeyboardButton(text=text.DELIVERY_TAXI)
delivery_spot_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
delivery_spot_kb.row(olc_button, taxi_button)
delivery_spot_kb.row(back_button)

share_phone_button = KeyboardButton(text=text.SHARE_PHONE_BTTN, request_contact=True)
share_phone_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
share_phone_kb.row(share_phone_button, back_button)


# kb for editing coffee menu
new_button = KeyboardButton(text=text.NEW)
edit_button = KeyboardButton(text=text.EDIT)
delete_button = KeyboardButton(text=text.DELETE)
show_all_button = KeyboardButton(text=text.SHOW_ALL)
edit_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
edit_menu_kb.row(show_all_button, edit_button)
edit_menu_kb.row(new_button, delete_button)
edit_menu_kb.row(back_button)

coffee_type_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
filter_button = KeyboardButton(text=text.FILTER)
espresso_button = KeyboardButton(text=text.ESPRESSO)
# both_button = KeyboardButton(text=text.BOTH)
coffee_type_kb.row(filter_button, espresso_button)
# coffee_type_kb.row(both_button)

buttons = []
grind_types_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
for item in text.GRIND_TYPES:
    buttons.append(KeyboardButton(text=item))

i = 0
while i < len(buttons):
    grind_types_kb.row(buttons[i], buttons[i + 1])
    i += 2
grind_types_kb.row(back_button)