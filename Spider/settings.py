# Settings

class Settings():
    MONGO_URI = "localhost:27017"
    MONGO_DB = "news"
    
    GENERAL_CRAWL_WAIT_TIME = 30*60
    
    SEBENARNYA_CRAWL_WAIT_TIME = 30*60 #in seconds
    SEBENARNYA_RAW_MONGO_COLLECTION = "sebenarnya_raw"
    SEBENARNYA_PRO_MONGO_COLLECTION = "sebenarnya_pro"  
    
    THESTAR_RAW_MONGO_COLLECTION = "thestar_raw"
    THESTAR_PRO_MONGO_COLLECTION = "thestar_pro"  
    
    METRO_RAW_MONGO_COLLECTION = "hmetro_raw"
    METRO_PRO_MONGO_COLLECTION = "hmetro_pro"  
    