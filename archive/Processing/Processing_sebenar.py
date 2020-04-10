import re
import json
import pandas as pd
import numpy as np
import requests
import collections
import time
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil import parser


class Processing:
    '''
    This class takes in a dictionary from mongodb News collection and parse the 
    content into a formatted json to be usa
    ed for the rest API
    '''
    def __init__(self, db_dict:dict):
        '''take input of dict retrieved from mongoDB
        '''
        self.scrap_date = datetime.now()
        self.raw = db_dict 
        self.date = parser.parse(db_dict['date'])
        self.url =  db_dict['url']
        self.title = self.raw['title']
        self.category = 'FakeNewsAlert'
        self.tag = 'COVID-19'
        self.fact_src, self.content_text, self.soup = self.parse_content()
        self.content_html = str(self.soup)
        self.label_map = self.get_label_map()
        self.label, self.confidence = self.get_label_n_confidence()
        self.audios, self.images = self.get_figures()
        self.json_file = self.to_json()
        
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
                    key_index = lines.index(next(keys_gen))
                    if i == 0:
   
            for line in lines[old_key_index+1:]:
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
    
    def to_json(self):
        json_file = dict(
            scrap_date = self.scrap_date
            news_date = self.date,
            url = self.url,
            title = self.title,
            category = self.category,
            tag = self.tag
            content_text = self.content_text,
            images = self.images,
            audios = self.audios,
            fact_src = self.fact_src,
            label = self.label,
            confidence = self.confidence,
            content_html = self.content_html,
        )
        return json_file