import re
import json
import pymongo
import pandas as pd
import numpy as np
import requests
import collections
import time
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil import parser
from settings import Settings

# 'dep_content_text': response.css('div.td-post-content p::text').getall(), #deprecated
# 'dep_img_src': response.css('div.td-post-content img::attr(src)').getall() #deprecated

def updater_processing_sebenarnya():
    MONGO_URI = Settings.MONGO_URI
    MONGO_DB = Settings.MONGO_DB
    RAW_COLLECTION = Settings.SEBENARNYA_RAW_MONGO_COLLECTION
    PRO_COLLECTION = Settings.SEBENARNYA_PRO_MONGO_COLLECTION
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    raw_coll = db[RAW_COLLECTION]
    pro_coll = db[PRO_COLLECTION]
    
    x = list(raw_coll.find({"processed_date": {"$exists": 0}}).limit(300))
    for j in x:
        raw_dict = j.copy()
        pro_dict = Processing_Sebenarnya(raw_dict).pro.copy()

        # Update raw collection with processed_date
        update = { "$set": { "processed_date": datetime.datetime.today() } }
        raw_coll.update_one(j, update)

        # Insert processed dict to processed collection
        pro_coll.insert_one(pro_dict)

    print("Done: Processing SEBENARNYA.", len(x))


class Processing_Sebenarnya:
    '''
    This class takes in a dictionary from mongodb News collection and parse the 
    content into a formatted json to be used for the rest API
    '''
    def __init__(self, db_dict:dict):
        '''take input of dict retrieved from mongoDB
        '''
        self.raw = db_dict
        self.pro = db_dict.copy()
        
        self.content_lines, self.fact_src, self.content_text, self.soup = self.parse_content()
        self.title = self.raw['title']
        self.label_map = self.get_label_map()
        self.label, self.confidence = self.get_label_n_confidence()
        self.audios, self.images = self.get_figures()
        
        # create processed dict
        self.run_processed() # self.pro
        
    def get_label_map(self):
        label_map = {
            '1' : ['tidak benar(:|.|$)', 'palsu(:|.|$)'],
            '2' : ['^waspada'],
            '3' : ['penjelasan(:|.|$)', '^makluman'],
        }
        return label_map
        
        
    def parse_content(self):
        content = self.raw['content_html']
        soup = BeautifulSoup(content[0], 'html.parser')
        rm_index = (soup.text.find(soup.find('div',{'class':'awac-wrapper'}).text) 
                    if soup.find('div',{'class':'awac-wrapper'}) else len(soup.text))
        all_text = soup.text[:rm_index]
        lines = [line.strip() for line in all_text.split('\n') if line.strip() != '']
        content_text = ' '.join(all_text.split('\n')).strip()
        
        r = re.compile("^SUMBER:$")
        keys = list(filter(r.match, lines))
        content_list =[]
        fact_src = []
        text_dict = {}
        if len(keys) > 0:
            key_index = lines.index(keys[0])
            key =  keys[0].strip(':').replace(' ', '_')
   
            for line in lines[key_index+1:]:
                fact_src.append({
                    'text' : line,
                    'link' : ('' if soup.find('a', href=True, text=line) is None
                              else soup.find('a', href=True, text=line)['href'])
                })
            

        return lines, fact_src, content_text, soup
   
    
    def get_label_n_confidence(self):
        keyword_found = []
        for key in self.label_map.keys():
            for regex in self.label_map[key]:
                if re.search(regex, self.title.lower()):
                    keyword_found.append(key)
                for line in self.content_lines:
                    if re.search(regex, line.lower()):
                        keyword_found.append(key)

        if len(keyword_found)==0:
            label = 1    # default label is 1
            confidence = 3 # if nothing is found give lowest confidence
        else:
            counter = collections.Counter(keyword_found)
            label = int(counter.most_common(1)[0][0])
            confidence = 1 if len(np.unique(keyword_found))==1 else 2
        return (label, confidence)
    
    def get_figures(self):
        audios = []
        images = []
        for figure in self.soup.find_all('figure'):
            if figure.find('audio') is not None:
                audios.append({
                    'src' : figure.find('audio').get('src'),
                    'caption' : [] if figure.find('figcaption') is None else figure.find('figcaption').text
                })
            if figure.find('img') is not None:
                images.append({
                    'src' : figure.find('img').get('src'),
                    'caption' : [] if figure.find('figcaption') is None else figure.find('figcaption').text
                })
        return audios, images
    
    
    def run_processed(self):
        # 1. scrape_date
        ## Done by default
        
        # 2. news_date
        self.pro['news_date'] = parser.parse(self.pro['news_date'])
        
        # 3. title
        ## Done by default
        
        # 4. category (news, or fake news alert)
        self.pro['category'] = 'FakeNewsAlert'
        
        # 5. topic (covid 19)
        self.pro['topic'] = 'COVID-19'
        
        # 6. content_text
        self.pro['content_text'] = self.content_text
        
        # 7. image { src, caption}
        self.pro['image'] = self.images,
            
        # 8. audio {src, caption}
        self.pro['audio'] = self.audios
        
        # 9. fact_src (NA if not fake news alert category)
        self.pro['fact_src'] = self.fact_src
        
        # 10. label (4 for actual reported news)
        self.pro['label'] = self.label
        
        # 11. confidence (4 for actual report news)
        self.pro['confidence'] = self.confidence
        
        # 12. url
        ## Done by default
        
        # 13. news_vendor
        ## Done by default
        
        # 14. content_html
        ## Done by default
        
        # 15. processed_date
        self.pro["processed_date"] = datetime.today()