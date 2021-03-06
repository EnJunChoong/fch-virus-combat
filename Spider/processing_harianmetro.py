import re
import pymongo
import pandas as pd
import numpy as np
import time
import datetime
from bs4 import BeautifulSoup
from settings import Settings
from elasticsearch import Elasticsearch


def updater_processing_harianmetro():
    MONGO_URI = Settings.MONGO_URI
    MONGO_DB = Settings.MONGO_DB
    RAW_COLLECTION = Settings.METRO_RAW_MONGO_COLLECTION
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    raw_coll = db[RAW_COLLECTION]
    # pro_coll = db[PRO_COLLECTION]
    
    ES_URI = Settings.ES_URI
    ES_INDEX_NAME = Settings.ES_INDEX_NAME
    es_conn = Elasticsearch(ES_URI)
    
    if not es_conn.indices.exists(index=ES_INDEX_NAME):
        es_conn.indices.create(index=ES_INDEX_NAME, ignore=400)
    
    x = list(raw_coll.find({"processed_date": {"$exists": 0}}).limit(500))
    for j in x:
        raw_dict = j.copy()
        
        try:
            pro_dict = Processing_HarianMetro(raw_dict).pro.copy()

            # Update raw collection with processed_date
            update = { "$set": { "processed_date": datetime.datetime.today() } }
            raw_coll.update_one(j, update)

            # Insert processed dict to processed collection
            # pro_coll.insert_one(pro_dict)
            print(f'processing {pro_dict["url"]}')
            doc_id = str(pro_dict['_id'])
            del pro_dict['_id']
            es_conn.create(index=ES_INDEX_NAME, body=pro_dict, id=doc_id)
            
        except Exception as err:
            print("Error at processing:", raw_dict.get("url"))
            print(err)
            
    print("Done: Processing HarianMetro.", len(x))


class Processing_HarianMetro:
    '''
    This class takes in a dictionary from mongodb News collection and parse the 
    content into a formatted json to be used for the rest API
    '''
    def __init__(self, db_dict:dict):
        '''take input of dict retrieved from mongoDB
        '''
        self.raw = db_dict
        self.pro = db_dict.copy()
        self.soup = None
        
        # create processed dict
        self.run_processed() # self.pro
        
        try:
            self.pro.pop("content_html")    
            self.pro.pop("meta_full_html")    
        except KeyError:
            print("Key not found")   
    
    def run_processed(self):
        self.soup = soup = BeautifulSoup(self.raw.get("content_html"), "html.parser")
        
        # 1. scrape_date
        ## Done by default
        
        # 2. news_date
        date_0 = soup.find("div", "published-date").get_text()
        date_1 = date_0.split(": ")[1].split(", ")[1]
        news_date = datetime.datetime.strptime(date_1, "%d %B %Y @ %I:%M %p")
        self.pro["news_date"] = news_date
        
        # 3. title
        title = soup.find("h1", "page-header").get_text()
        self.pro["title"] = title
        
        # 4. category (News, or FakeNewsAlert)
        category = "News"
        self.pro["category"] = category
        
        # 5. topic (COVID-19)
        topic = "COVID-19"
        self.pro["topic"] = topic
        
        # 6. content_text
        text_list = [j.get_text() for j in soup.find("div", "field-item even").find_all("p")]
        text_list = [j for j in text_list if j != ""]
        content_text = " ".join(text_list)
        self.pro["content_text"] = content_text
        
        # 7. image: list:{src, caption}
        if soup.find("img") is not None:
            src = soup.find("img").get("src")
            caption = soup.find("img").get("alt")
            image = [{"src": src, "caption": caption}]
            self.pro["image"] = image
        
        # 8. audio: list:{src, caption}
        audio = []
        self.pro["audio"] = audio
        
        ### PING IF FOUND!
        if soup.find("audio") is not None:
            print("======================")
            print("Harian Metro: FOUND AUDIO...")
            print("URL:", self.raw.get("url"))
            print("======================")
            
        # 9. fact_src (NA if not fake news alert category)
        self.pro["fact_src"] = []
        
        # 10. label (4 for actual reported news)
        label = 4
        self.pro["label"] = label
        
        # 11. confidence (4 for actual report news)
        confidence = 4
        self.pro["confidence"] = confidence
        
        # 12. url
        ## Done by default
        
        # 13. news_vendor
        ## Done by default
        
        # 14. content_html
        ## Done by default
        
        # 15. processed_date
        processed_date = datetime.datetime.today()
        self.pro["processed_date"] = processed_date
        
        

        
        

        
        
        


    