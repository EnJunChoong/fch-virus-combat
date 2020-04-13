import pymongo
from settings import Settings

def reset_raw_collection():
    MONGO_URI = Settings.MONGO_URI
    MONGO_DB = Settings.MONGO_DB
    RAW_COLLECTION_LIST = [Settings.METRO_RAW_MONGO_COLLECTION, Settings.THESTAR_RAW_MONGO_COLLECTION, Settings.SEBENARNYA_RAW_MONGO_COLLECTION]
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    for RAW_COLLECTION in RAW_COLLECTION_LIST:
        raw_coll = db[RAW_COLLECTION]
        update = { "$unset": { "processed_date": None } }
        raw_coll.update_many({}, update)
    print("Done: Reset processed_date...")
    
reset_raw_collection()