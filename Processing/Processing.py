import re
import json
import pandas as pd
import numpy as np
import requests
import collections
from bs4 import BeautifulSoup
from dateutil import parser


class Processing:
    '''
    This class takes in a dictionary from mongodb News collection and parse the 
    content into a formatted json to be used for the rest API
    '''
    def __init__(self, db_dict:dict):
        '''take input of dict retrieved from mongoDB
        '''
        self.raw = db_dict 
        self.date = parser.parse(db_dict['date'])
        self.url =  db_dict['url']
        self.title = self.raw['title']
        self.category = 'COVID-19'
        self.content_text, self.content_lines, self.fact_src, self.search_text, self.soup = self.parse_content()
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
        search_text = ' '.join(all_text.split('\n')).strip()
        
        r = re.compile("[A-Z]*:$")
        keys = list(filter(r.match, lines))
        keys_gen = iter(keys)
        content_list =[]
        fact_src = []
        old_key_index = 0
        text_dict = {}
        if len(keys) > 0:
            for i, key in enumerate(keys):
                text_dict = {}
                key = key.strip(':').replace(' ', '_')
                try:
                    new_key_index = lines.index(next(keys_gen))
                    if i == 0:
                        if new_key_index == 0:
                            try:
                                new_key_index = lines.index(next(keys_gen))
                                text_dict['header'] = key
                                text_dict['text'] = '\n'.join(lines[1:new_key_index])
                            except Exception as e:
                                pass
                        else:
                            text_dict['header'] = 'FREE_TEXT'
                            text_dict['text'] = '\n'.join(lines[1:new_key_index])
                    else:
                        text_dict['header'] = key
                        text_dict['text'] = '\n'.join(lines[old_key_index+1:new_key_index])
                except Exception as e:
                    pass
                old_key_index = new_key_index
                if len(text_dict) > 0:
                    content_list.append(text_dict)
                
            if re.match(re.compile('^sumber'), key.lower()):
                for line in lines[old_key_index+1:]:
                    fact_src.append({
                        'text' : line,
                        'link' : ('' if soup.find('a', href=True, text=line) is None
                                  else soup.find('a', href=True, text=line)['href'])
                    })
            else:
                text_dict['header'] = key
                text_dict['text'] = '\n'.join(lines[old_key_index+1:])
                content_list.append(text_dict)
        else:
            text_dict['free_text'] = '\n'.join(lines)
            content_list.append(text_dict)

        return content_list, lines, fact_src, search_text, soup
   
    
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
            date = self.date,
            category = self.category,
            url = self.url,
            title = self.title,
            content_text = self.content_text,
            images = self.images,
            audios = self.audios,
            fact_src = self.fact_src,
            label = self.label,
            confidence = self.confidence,
            search_text = self.search_text,
            content_html = self.content_html,
        )
        return json_file