import scrapy
import pymongo
import logging
import time
from scrapy import signals, Request
from scrapy.exceptions import DontCloseSpider, CloseSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def check_to_scrap(url, coll):
    x = coll.find_one({'url': url}, { "_id": 1})
    if x is None:
        return True
    else: 
        return False
    
class MySpider(scrapy.Spider):
    name = 'sebenarnya_v2'
    start_urls = ['https://www.malaysiakini.com/stories/covid19']
    check_pg = 0
    pg = 0
    num = 0
    MAX_CHECK_PAGE = 3
    MONGO_URI = "localhost:27017"
    MONGO_DATABASE = "news"
    SEBENARNYA_COLLECTION = "sebenarnya_v2_test1"
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MySpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=crawler.settings.get('MONGO_URI'),
        cls.mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        cls.collection_name = crawler.settings.get("SEBENARNYA_COLLECTION")
                
        cls.mongo_uri=cls.MONGO_URI
        cls.mongo_db=cls.MONGO_DATABASE
        cls.collection_name = cls.SEBENARNYA_COLLECTION
        
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    def parse(self, response):
        news_links = response.css('div.news a::attr(href)').getall() 
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
        
        item = {
            'date': response.css('div.td-post-header time.entry-date::attr(datetime)').get(),
            'title': extract_with_css('.entry-title::text'),
            'content_html': response.css('div.td-post-content').getall(),
            'url': response.url,
            'label': 'placeholder',
            'confidence': 'placeholder',
            'category': 'placeholder',
            
            'meta_full_html': response.text,
            
            'dep_content_text': response.css('div.td-post-content p::text').getall(), #deprecated
            'dep_img_src': response.css('div.td-post-content img::attr(src)').getall() #deprecated

            }
        self.coll.insert_one(dict(item))
        yield {}
        
