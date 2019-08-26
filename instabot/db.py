import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.test
insta = db.insta
users = db.users

def add_user(user_id):
    users.insert_one({"user_id" : user_id, "is_update" : False, "delay" : 720})


def check_user(user_id):
    return users.count_documents({"user_id" : user_id})

def get_user(user_id):
    return users.find_one({"user_id": user_id})

def update_settings(user_id, settings, param):
    users.update_one({'user_id':user_id},{'$set': {settings:param}})


def add_account(account):
    data = {"account": account}
    cursor = insta.count_documents(data)
    if cursor == 0:
        try:
           insta.insert_one(data)
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
        acc = insta.find({}, {"account":1})
        l = []
        for a in acc:
            l.append(a["account"])
        return l
    except Exception as e:
        print(e)


def del_account(account):
    try:
        #accounts.delete_one({'account' : account})
        insta.delete_one({'account' : account})
        #return r.deleted_count
    except Exception as e:
        print(e)

def get_media():
    try:
        media = insta.find({})
        return media
    except Exception as e:
        print(e)