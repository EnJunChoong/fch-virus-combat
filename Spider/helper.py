import pymongo

def check_to_scrap(url, coll):
    x = coll.find_one({'url': url}, { "_id": 1})
    if x is None:
        return True
    else: 
        return False
    
def quick_list_collection():
    MONGO_URI = "localhost:27017"
    MONGO_DB = "news"
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    colls = list(db.list_collection_names())

    z = []
    for MONGO_COLLECTION in colls:
        coll = db[MONGO_COLLECTION]
        x = list(coll.find())
        n = len(x)
        z.append({"n": n, "coll":MONGO_COLLECTION})
    return pd.DataFrame(z)

def create_index():
    #     coll.create_index([("url", "text"), ("title", "text"), ("search_text", "text")])
    #     list(coll.list_indexes())
    #     list(coll.find({"$text":{"$search": "Hebahan"}}))
    pass