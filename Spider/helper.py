import pymongo

def check_to_scrap(url, coll):
    x = coll.find_one({'url': url}, { "_id": 1})
    if x is None:
        return True
    else: 
        return False