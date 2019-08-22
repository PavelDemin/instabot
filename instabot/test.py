import requests

fileURL = "https://www.instagram.com/papyasishe1/"

f = requests.get(fileURL)

print(f.status_code)