import asyncio
import logging
import aiohttp
import requests
import os
from instagram import Account, Media, WebAgent
import db

import time
#from time import time

#https://surik00.gitbooks.io/aiogram-lessons/content/chapter5.html
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.markdown import text
from aiogram.dispatcher import Dispatcher
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

PROXY_URL = 'http://181.177.86.88:9556'
PROXY_AUTH = aiohttp.BasicAuth(login='9tFhcM', password='w91adS')
# If authentication is required in your proxy then uncomment next line and change login/password for it
# PROXY_AUTH = aiohttp.BasicAuth(login='login', password='password')
# And add `proxy_auth=PROXY_AUTH` argument in line 25, like this:
# >>> bot = Bot(token=API_TOKEN, loop=loop, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
# Also you can use Socks5 proxy but you need manually install aiohttp_socks package.

API_TOKEN = '913359177:AAHUTfYP1bwiDkrcMagJAAS6UWi0HY3EFJE'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
#loop = asyncio.get_event_loop()
#bot = Bot(token=API_TOKEN, loop=loop, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
bot = Bot(token=API_TOKEN)
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


async def printer():
    num = 1
    while True:
        print(num)
        num += 1
        await asyncio.sleep(1)

def check_account(account):
    r = requests.get(insta_url + account)
    return r.status_code


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
   # await message.text("Welcome to Instagram Media Save Bot!")
    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Обновить', "Настройки")
    markup.add('Обновить', u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, "Выбирете пункт меню:", reply_markup=markup)


@dp.message_handler(lambda message: message.text and 'обновить' in message.text.lower())
async def update(message: types.Message):
    await bot.send_message(message.chat.id, 'Идет загрузка новых публикаций...')
    if(load_media()) > 0:
        media = db.get_media()
        for m in media:
            await bot.send_message(message.chat.id, 'Публикация от ' + m['account'] + '\n' + insta_url + 'p/' + m['mediaId'])
    else:
        await bot.send_message(message.chat.id, 'Новых публикаций нет!')


@dp.message_handler(lambda message: message.text and u'\U0001F464 аккаунты' in message.text.lower())
async def list_accounts(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(u'\U00002795 Добавить', u'\U00002796 Удалить')
    markup.add('Обновить', u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, 'Список аккаунтов:\n' + '\n'.join(db.get_accounts()), reply_markup=markup)


@dp.message_handler(lambda message: message.text and u'\U00002795 добавить' in message.text.lower())
async def add_account_to_list(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Обновить', u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, 'Введите новый аккаунт:', reply_markup=markup)


@dp.message_handler(lambda message: message.text and u'\U00002796 удалить' in message.text.lower())
async def process_command_1(message: types.Message):
    await message.reply("Первая инлайн кнопка", reply_markup=inline_kb1)


@dp.message_handler(commands=['1'])
async def process_command_1(message: types.Message):
    
    for  acc in db.get_accounts():
        print(acc)
        btn = (InlineKeyboardButton(str(acc), callback_data='button1'))
        print(btn)
    inline_kb1 = InlineKeyboardMarkup().add(btn)
    await message.reply("Первая инлайн кнопка", reply_markup=inline_kb1)


@dp.message_handler(regexp='^[A-Za-z0-9_.]{1,30}$')
async def get_account_name(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Обновить', u'\U0001F464 Аккаунты')
    if check_account(message.text) == 200:
        db.add_account(message.text)
        await bot.send_message(message.chat.id, 'Аккаунт добавлен! \nВведите новый аккаунт:', reply_markup=markup)
    else:
        await bot.send_message(message.chat.id, 'Имя аккаунта не корректно \nПопробуйте еще раз:', reply_markup=markup)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    tasks = [
        loop.create_task(printer()),
        executor.start_polling(dp)
    ]
