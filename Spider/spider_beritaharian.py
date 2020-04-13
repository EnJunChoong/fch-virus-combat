import os
import time
import datetime
import pymongo
import scrapy
import logging
from scrapy import signals, Request
from scrapy.exceptions import DontCloseSpider, CloseSpider
from scrapy_splash import SplashRequest

from helper import check_to_scrap
from settings import Settings

class BeritaHarianSpider(scrapy.Spider):
    name = "BeritaHarian"
    domain = 'https://www.bharian.com.my'
    MONGO_URI = Settings.MONGO_URI
    MONGO_DATABASE = Settings.MONGO_DB
    BHARIAN_COLLECTION_COVID = Settings.BHARIAN_RAW_MONGO_COLLECTION
    
    check_pg = 0
    MAX_CHECK_PAGE = 3
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BeritaHarianSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=cls.MONGO_URI
        cls.mongo_db=cls.MONGO_DATABASE
        cls.collection_name = cls.BHARIAN_COLLECTION_COVID
        
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    def start_requests(self):     
        urls = [
            'https://www.bharian.com.my/search?s=covid'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_links)    
    
    def parse_links(self, response):
        body = response.css('div.region-content div.block-content')
        articles = body.css('div.views-field-title')
        article_links = [self.domain+article.css('a::attr(href)').get() 
                         for article in articles
                         if len(article.css('a::attr(href)').get()) > 0
                        ]
        
        article_links_filtered = [j for j in article_links if check_to_scrap(j, self.coll)]
        print(article_links_filtered)
        if len(article_links_filtered) == 0:
            self.check_pg += 1
            if self.check_pg >= self.MAX_CHECK_PAGE:
                raise CloseSpider #Exception("End")
                
        yield from response.follow_all(article_links_filtered, self.parse_news)
        
        paginationlink = response.css('li.pager-next a::attr(href)').getall()
 
        if len(paginationlink) > 0:
            page = paginationlink[0]
            nextlink = self.domain+'/search?s=koronavirus&'+ page
            print('############')
            print(nextlink)
            print('############\n')
            yield from response.follow_all([nextlink], self.parse_links)
            

    def parse_news(self, response):
        time.sleep(1)
        
        body = response.css('section.col-sm-8').get()
        body = body[:body.find('div class="region region-content-bottom">')]
        date_raw = response.css('div.node-meta::text').get()
        linkname = os.path.basename(response.url)
        filename = linkname+'.html'
        url = response.url        
        
        result_dict = {
            'scrape_date': datetime.datetime.today(),
            'news_date': date_raw,
            'title': '',
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
            'content_html': body,
            'meta_full_html': response.text
        }
        self.coll.insert_one(result_dict)