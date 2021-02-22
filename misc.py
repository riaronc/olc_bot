#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import wfp
import sqlite
from menu import Menu


logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_API)
memory_storage = MemoryStorage()
dp = Dispatcher(bot, storage=memory_storage)
db = sqlite.SQLite(database=config.DB)
wfp = wfp.WayForPay()
menu = Menu()
db.get_menu(menu)
inline_items = []
