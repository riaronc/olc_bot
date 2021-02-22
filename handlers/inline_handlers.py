#!/usr/bin/env python
# -*- coding: utf-8 -*-

from misc import dp, bot, menu, inline_items, db
from menu import InlineMenuItem


@dp.inline_handler()
async def show_menu(query):
    await bot.answer_inline_query(query.id, menu.show_menu(query), cache_time=10)


@dp.callback_query_handler()
async def add_item_to_cart(query):
    for inline_item in inline_items:
        if inline_item.inline_id == query["inline_message_id"]:
            selected_item = inline_item.item
            db.add_to_cart(user_id=query["from"].id, item=selected_item)
            await bot.answer_callback_query(query.id, "✅ додано до кошика")
    await bot.answer_callback_query(query.id, "💔 сталася помилка")


@dp.chosen_inline_handler()
async def chose_inline_item(query):
    selected_item = menu.get_selected_item(menu_type=query['query'], id=query['result_id'])
    inline_items.append(InlineMenuItem(item=selected_item, inline_id=query["inline_message_id"]))