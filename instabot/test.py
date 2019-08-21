import requests
import aiohttp


PROXY_URL = 'http://181.177.86.88:9556'
PROXY_AUTH = aiohttp.BasicAuth(login='9tFhcM', password='w91adS')
# If authentication is required in your proxy then uncomment next line and change login/password for it
# PROXY_AUTH = aiohttp.BasicAuth(login='login', password='password')
# And add `proxy_auth=PROXY_AUTH` argument in line 25, like this:
# >>> bot = Bot(token=API_TOKEN, loop=loop, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
# Also you can use Socks5 proxy but you need manually install aiohttp_socks package.

API_TOKEN = '913359177:AAHUTfYP1bwiDkrcMagJAAS6UWi0HY3EFJE'

fileURL = "https://www.instagram.com/papyasishe1/"

f = requests.get(fileURL)

print(f.status_code)