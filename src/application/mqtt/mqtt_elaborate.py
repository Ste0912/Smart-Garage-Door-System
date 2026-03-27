import json, os
from datetime import datetime
from pymongo import MongoClient

def connect_to_DB():
    client_uri=f'{os.getenv("DB_PROTOCOL")}://{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/'
    client = MongoClient(client_uri)
    if client is None:
        print("MongoDB connection failed")
        return None, None
    db = client[os.getenv("DB_NAME")]
    if db is None:
        return None, None
    return client, db

def find_user_by_uid(uid, db, collection):
    found = None
    id = None
    collection_obj = db[collection]
    for element in collection_obj.find():
        json_element = json.loads(json.dumps(element, default=str))
        if json_element["profile"]["uid"] == uid:
            if collection == 'pedestrians':
                found = json_element["profile"]["username"]
            elif collection == 'cars':
                found = json_element["profile"]["reg_plate"]
            id=json_element["_id"]
            return found, id
    return found, id

def handle_enter_exit(payload, db, msg):
    try:
        uid = payload.get("uid", None)
    except:
        return {
            "action" : "Nothing",
            "params": {}
        }
    found = None
    id = None

    found, id = find_user_by_uid(uid, db, 'pedestrians')
    collection = 'pedestrians'
    if found is None:
        found, id = find_user_by_uid(uid, db, 'cars')
        collection = 'cars'

    if found is None:
        return {
            "action" : "MQTT and CLEAR",
            "params":{
                "topic" : msg.topic,
                "payload": f'ERROR Non authorised'
            }
        }
    else:
        open=msg.topic.replace(os.getenv("DB_NAME") + "/", "").upper()
        collection = db[collection]

        if open=="ENTER":
            collection.update_one({"_id": id}, {"$push": {"data.enter" : datetime.now()}})
            collection.update_one({"_id": id}, {"$set": {"profile.atHome" : True}})
        elif open=="EXIT":
            collection.update_one({"_id": id}, {"$push": {"data.exit" : datetime.now()}})
            collection.update_one({"_id": id}, {"$set": {"profile.atHome" : False}})
    
        return {
            "action" : "MQTT and CLEAR",
            "params":{
                "topic" : msg.topic,
                "payload": f'{open} {found}'
            }
        }

def elaborate_mqtt(msg):
    payload = json.loads(msg.payload.decode())
    client, db = connect_to_DB()
    if client is None:
        print("MongoDB connection failed")
        return {
            "action" : "Nothing",
            "params": {}
        }

    if msg.topic == os.getenv("DB_NAME") + "/exit" or msg.topic == os.getenv("DB_NAME") + "/enter":
        return handle_enter_exit(payload, db, msg)