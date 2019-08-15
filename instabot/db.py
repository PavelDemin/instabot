from instagram import Account, Media, WebAgent
import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

agent = WebAgent()
db = client.test
insta = db.insta
accounts = db.accounts

def add_account(account):
    data = {"account": account}
    cursor = accounts.count_documents(data)
    if cursor == 0:
        try:
            acc = Account(account)
            media_file = agent.get_media(acc, count=1)
            accounts.insert_one(data)
        except Exception as msg:
            print(msg)
    else:
        raise Exception("Такой пользователь уже есть")


def update_media(data):
    insta.insert_one(data)

def count_media(data):
    return insta.count_documents({"mediaId": data})

def get_accounts():
    try:
        acc = accounts.find({}, {"account":1})
        l = []
        for a in acc:
            l.append(a["account"])
        return l
    except Exception as e:
        print(e)



def get_media():
    try:
        media = insta.find({}, {"filename":1})
        l = []
        for m in media:
            l.append(m["filename"])
        return l
    except Exception as e:
        print(e)