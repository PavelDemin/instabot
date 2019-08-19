import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.test
insta = db.insta
accounts = db.accounts

def add_account(account):
    data = {"account": account}
    cursor = accounts.count_documents(data)
    if cursor == 0:
        try:
           accounts.insert_one(data)
        except Exception as msg:
            print(msg)
    else:
        raise Exception("Такой пользователь уже есть")


def update_media(data):
    try:
        insta.replace_one({'account' : data['account']},{'account' : data['account'], 'mediaId' : data['mediaId']}, True)
    except Exception as e:
        print(e)

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


def del_account(account):
    try:
        r = accounts.delete_one({'account' : account})
        return r.deleted_count
    except Exception as e:
        print(e)

def get_media():
    try:
        media = insta.find({})
        return media
    except Exception as e:
        print(e)