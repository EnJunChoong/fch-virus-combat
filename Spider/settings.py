# Settings

class Settings():
    MONGO_URI = "localhost:27017"
    MONGO_DB = "news"
    ES_URI = "localhost:9200"
    ES_INDEX_NAME = "all_news"
    
    
    GENERAL_CRAWL_WAIT_TIME = 30*60
    
    SEBENARNYA_CRAWL_WAIT_TIME = 30*60 #in seconds
    SEBENARNYA_RAW_MONGO_COLLECTION = "sebenarnya_raw"
    
    THESTAR_RAW_MONGO_COLLECTION = "thestar_raw"
    
    METRO_RAW_MONGO_COLLECTION = "hmetro_raw"
    
    BHARIAN_RAW_MONGO_COLLECTION = 'bharian_raw'
    