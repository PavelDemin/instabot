import asyncio
import logging
import aiohttp
import urllib.request
from bs4 import BeautifulSoup
import datetime
from instagram import Account, Media, WebAgent
import db

from aiogram import Bot, Dispatcher, executor, types

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
loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop)
dp = Dispatcher(bot)
#import pdb; pdb.set_trace()
agent = WebAgent()

path = "./media/"
insta_url = "https://www.instagram.com/p/"

# https://github.com/Sunil02324/Instagram-Image-Downloader
def DownloadSingleFile(fileURL):
    print ('Downloading image...')
    f = urllib.request.urlopen(fileURL)
    htmlSource = f.read()
    soup = BeautifulSoup(htmlSource,'html.parser')
    metaTag = soup.find_all('meta', {'property':'og:image'})
    imgURL = metaTag[0]['content']
    file_name = path + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '.jpg'
    urllib.request.urlretrieve(imgURL, file_name)
    print ('Done. Image saved to disk as ' + file_name)
    return file_name

def load_media():
    info = []
    for account in db.get_accounts():
        acc = Account(account)
        media_file = agent.get_media(acc, count=1)
        media_id = str(media_file[0][0])
        url1 = insta_url + media_id
        if db.count_media(media_id) == 0:
            file_name = DownloadSingleFile(url1)
            info.append([media_id, file_name])
            insta_info = {
                "account": account,
                "filename": file_name,
                "mediaId": media_id
            }
            db.update_media(insta_info)
        else:
            continue


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
   # await message.text("Welcome to Instagram Media Save Bot!")
    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Обновить', "Настройки")
    markup.add(u'\U0001F464 Аккаунты')

    await bot.send_message(message.chat.id, "Выбирете пункт меню:", reply_markup=markup)


@dp.message_handler(lambda message: message.text and 'обновить' in message.text.lower())
async def update(message: types.Message):
    await bot.send_message(message.chat.id, 'Идет загрузка новых публикаций...')
    load_media()
    media = db.get_media()
    for m in media:
        with open('media\\'+m, 'rb') as photo:
            await bot.send_document(message.chat.id, photo)

@dp.message_handler(lambda message: message.text and u'\U0001F464 аккаунты' in message.text.lower())
async def update(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(u'\U00002795 Добавить', u'\U00002796 Удалить')
    markup.add(u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, 'Список аккаунтов:\n' + '\n'.join(db.get_accounts()), reply_markup=markup)


@dp.message_handler(lambda message: message.text and u'\U00002795 добавить' in message.text.lower())
async def update(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Обновить', u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, 'Введите новый аккаунт:', reply_markup=markup)

@dp.message_handler(regexp='^[A-Za-z0-9_.]{1,30}$')
async def msg_handler(message: types.Message):
    db.add_account(message.text)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('Обновить', u'\U0001F464 Аккаунты')
    await bot.send_message(message.chat.id, 'Аккаунт добавлен! \nВведите новый аккаунт:', reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)