import os
import time
import datetime
import pymongo
import scrapy
import logging
from scrapy import signals, Request
from scrapy.exceptions import DontCloseSpider, CloseSpider

from helper import check_to_scrap
from settings import Settings


    
class SebenarnyaSpider(scrapy.Spider):
    name = 'sebenarnya' #v2
    start_urls = ['https://sebenarnya.my/category/novel-coronavirus-2019-ncov/']
    check_pg = 0
    pg = 0
    num = 0
    MAX_CHECK_PAGE = 3
    MONGO_URI = Settings.MONGO_URI
    MONGO_DATABASE = Settings.MONGO_DB
    SEBENARNYA_COLLECTION = Settings.SEBENARNYA_RAW_MONGO_COLLECTION
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SebenarnyaSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=cls.MONGO_URI
        cls.mongo_db=cls.MONGO_DATABASE
        cls.collection_name = cls.SEBENARNYA_COLLECTION
        
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    def parse(self, response):
        news_links = response.css('div.td-pb-span8 .entry-title a::attr(href)').getall() 
        news_links_filtered = [j for j in news_links if check_to_scrap(j, self.coll)]
        if len(news_links_filtered) == 0:
            self.check_pg += 1
            if self.check_pg >= self.MAX_CHECK_PAGE:
                raise CloseSpider #Exception("End")
                
        yield from response.follow_all(news_links_filtered, self.parse_news)

        pagination_links = response.css('.page-nav a')

        if len(pagination_links) == 1:
            yield from response.follow_all(pagination_links, self.parse)
            self.pg += 1
        elif len(pagination_links) == 2:
            yield from response.follow_all(pagination_links[1:2], self.parse)
            self.pg += 1
        else:
            print("End:", response.url)

    def parse_news(self, response):
        self.num += 1
        def extract_with_css(query):
            return response.css(query).get(default='').strip()
        
        news_date_raw = response.css('div.td-post-header time.entry-date::attr(datetime)').get()
        title_raw = extract_with_css('.entry-title::text')
        item = {
            'scrape_date': datetime.datetime.today(),
            'news_date': news_date_raw,
            'title': title_raw,
            'category': '',
            'topic': '',
            'content_text': '',
            'images': [],
            'audio': [],
            'fact_src': '',
            'label': '',
            'confidence': '',
            'url': response.url,
            'news_vendor': self.name,
            'content_html': response.css('div.td-post-content').getall(),
            'meta_full_html': response.text
            }
        
        self.coll.insert_one(item)
        yield {}
        
