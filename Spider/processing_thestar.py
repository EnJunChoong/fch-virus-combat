import re
import json
import pymongo
import pandas as pd
import numpy as np
import requests
import collections
import time
import datetime
from bs4 import BeautifulSoup
from dateutil import parser
from settings import Settings

def updater_processing_thestar():
    MONGO_URI = Settings.MONGO_URI
    MONGO_DB = Settings.MONGO_DB
    RAW_COLLECTION = Settings.THESTAR_RAW_MONGO_COLLECTION
    PRO_COLLECTION = Settings.THESTAR_PRO_MONGO_COLLECTION
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    raw_coll = db[RAW_COLLECTION]
    pro_coll = db[PRO_COLLECTION]
    
    x = list(raw_coll.find({"processed_date": {"$exists": 0}}).limit(300))
    for j in x:
        raw_dict = j.copy()
        
        try:
            pro_dict = Processing_TheStar(raw_dict).pro.copy()
            
            # Insert processed dict to processed collection
            pro_coll.insert_one(pro_dict)
            
            # Update raw collection with processed_date
            update = { "$set": { "processed_date": datetime.datetime.today() } }
            raw_coll.update_one(j, update)

        except Exception as err:
            print("Error at processing:", raw_dict.get("url"))
            print(err)
            
    print("Done: Processing TheStar.", len(x))


class Processing_TheStar:
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
        dd = soup.find("p", "date").get_text().strip().split(",")[1].strip()
        tt_soup = soup.find("time", "timestamp")
        if tt_soup is not None:
            tt = tt_soup.get_text().split(" MYT")[0]
            dt_str = dd + " " + tt
            news_date = datetime.datetime.strptime(dt_str, "%d %b %Y %I:%M %p")
        else:
            news_date = datetime.datetime.strptime(dd, "%d %b %Y")
            
        self.pro["news_date"] = news_date
            
        
        # 3. title
        title = soup.find("div", "headline story-pg").find("h1").get_text().strip()
        self.pro["title"] = title
        
        # 4. category (News, or FakeNewsAlert)
        category = "News"
        self.pro["category"] = category
        
        # 5. topic (COVID-19)
        topic = "COVID-19"
        self.pro["topic"] = topic
        
        # 6. content_text
        z = soup.find("div", "story")
        _ = [x.extract() for x in z.findAll('script')]
        content_text = z.get_text().strip().replace("\n", "")
        self.pro["content_text"] = content_text
        
        # 7. image: list:{src, caption}
        soup_img = soup.find("div", "story-image")
        if soup_img.find("img") is not None:
            src = soup_img.find("img").get("src")
            caption = soup_img.find("p", "caption")
            if caption is not None:
                caption = caption.get_text()
            image = [{"src": src, "caption": caption}]
        else:
            image = []
        self.pro["image"] = image
        
        # 8. audio: list:{src, caption}
        audio = []
        self.pro["audio"] = audio
        
        ### PING IF FOUND!
        if soup.find("audio") is not None:
            print("======================")
            print("TheStar: FOUND AUDIO...")
            print("URL:", self.raw.get("url"))
            print("======================")
            
        # 9. fact_src (NA if not fake news alert category)
        ## Done by default
        
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
        
         
