import asyncio
import logging
import aiohttp
import requests
import os
from instagram import Account, Media, WebAgent
import db
import config as cfg

import time
#from time import time

#https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.markdown import text
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.background import BackgroundScheduler

#my_chat_id = 228534214

# Configure logging
#logging.basicConfig(filename="log.log", level=logging.WARNING)
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
loop = asyncio.get_event_loop()
bot = Bot(token=cfg.API_TOKEN, proxy=cfg.PROXY_URL, proxy_auth=cfg.PROXY_AUTH)
#bot = Bot(token=cfg.API_TOKEN)
dp = Dispatcher(bot)
#import pdb; pdb.set_trace()
agent = WebAgent()

insta_url = "https://www.instagram.com/"

def load_media():
    count = 0
    for account in db.get_accounts():
        acc = Account(account)
        media_file = agent.get_media(acc, count=1)
        media_id = str(media_file[0][0])
        if db.count_media(media_id) == 0:
            insta_info = {
                "account": account,
                "mediaId": media_id
            }
            db.update_media(insta_info)
            count += 1
        else:
            continue
    return count

#def dell(account):
#    db.del_account(account)
#    print('Del '+ account)

#for account in db.get_accounts():
#    dell(account)

async def update_media(my_chat_id):
    if load_media() > 0:
        media = db.get_media()
        for m in media:
            await bot.send_message(my_chat_id, 'Публикация от ' + m['account'] + '\n' + insta_url + 'p/' + m['mediaId'])


def check_account(account):
    r = requests.get(insta_url + account)
    return r.status_code


#@dp.callback_query_handler(lambda c: c.data == 'delate')
@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    #print(callback_query)
    if callback_query.data.startswith('delate'):
        acc = callback_query.data.split('=')[-1]
        db.del_account(acc)
        await bot.answer_callback_query(callback_query.id, text = 'Аккаунт ' + acc + ' удален!')
    #    await account_manager(callback_query.message)
        inline_kb1 = InlineKeyboardMarkup(row_width=2)
        for  acc in db.get_accounts():
            btn1 = InlineKeyboardButton(acc, callback_data=acc)
            btn = InlineKeyboardButton(u'\U0000274C', callback_data='delate='+acc)
            inline_kb1.row(btn1, btn)
        await bot.edit_message_text(text = '<b>Управление аккаунтами</b>\nДля того чтобы добавить аккаунт, напишите боту его имя.', chat_id = callback_query.message.chat.id, message_id = callback_query.message.message_id, reply_markup=inline_kb1, parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
   # await message.text("Welcome to Instagram Media Save Bot!")
    # Configure ReplyKeyboardMarkup
    
    my_chat_id = message.chat.id
   # print(my_chat_id)
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: loop.create_task(update_media(my_chat_id)), "interval", seconds=20)
    scheduler.start()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(u'\U0001F504 Обновить', "Настройки")
    markup.add(u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, "Выбирете пункт меню:", reply_markup=markup)


@dp.message_handler(lambda message: message.text and u'\U0001F504 обновить' in message.text.lower())
async def update(message: types.Message):
    await bot.send_message(message.chat.id, 'Идет загрузка новых публикаций...')
    if load_media() > 0:
        media = db.get_media()
        for m in media:
            await bot.send_message(message.chat.id, 'Публикация от ' + m['account'] + '\n' + insta_url + 'p/' + m['mediaId'])
    else:
        await bot.send_message(message.chat.id, 'Новых публикаций нет!')


@dp.message_handler(lambda message: message.text and u'\U0001F464 аккаунты' in message.text.lower())
async def account_manager(message: types.Message):
    inline_kb1 = InlineKeyboardMarkup(row_width=3)
    #inline_kb1.add(InlineKeyboardButton('Добавить аккаунт', callback_data='add'))
    for  acc in db.get_accounts():
        btn1 = InlineKeyboardButton(acc, callback_data=acc)
        btn = InlineKeyboardButton(u'\U0000274C', callback_data='delate='+acc)
        inline_kb1.row(btn1, btn)
    await bot.send_message(message.chat.id, '<b>Управление аккаунтами</b>\nДля того чтобы добавить аккаунт, напишите боту его имя.', reply_markup=inline_kb1, parse_mode='HTML')

@dp.message_handler(lambda message: message.text and u'\U00002795 добавить' in message.text.lower())
async def add_account_to_list(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(u'\U0001F504 Обновить', u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, 'Введите новый аккаунт:', reply_markup=markup)


@dp.message_handler(regexp='^[A-Za-z0-9_.]{1,30}$')
async def get_account_name(message: types.Message):
    if check_account(message.text) == 200:
        db.add_account(message.text)
        await account_manager(message)
    else:
        await bot.send_message(message.chat.id, '<b>Имя аккаунта не корректно!</b> \nПопробуйте еще раз.', parse_mode='HTML')

if __name__ == '__main__':
    #loop = asyncio.get_event_loop()
    
    executor.start_polling(dp)

