import scrapy
import pymongo
import logging
import time
from scrapy import signals, Request
from scrapy.exceptions import DontCloseSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from .sebenar_spider_v1 import MySpider

# def check_to_scrap(url, coll):
#     x = coll.find_one({'url': url}, { "_id": 1})
#     if x is None:
#         return True
#     else: 
#         return False
    
# class MySpider(scrapy.Spider):
#     name = 'sebenarnya_v1_test3'
#     start_urls = ['https://sebenarnya.my/category/novel-coronavirus-2019-ncov/page/19']
#     pg = 0
#     num = 0
#     MONGO_URI = "localhost:27017"
#     MONGO_DATABASE = "news"
#     SEBENARNYA_COLLECTION = "sebenarnya_v1_test2"
#     RECRAWL_FREQUENCY = 30 # after 30 seconds crawl the same page again
    
#     @classmethod
#     def from_crawler(cls, crawler, *args, **kwargs):
#         spider = super(MySpider, cls).from_crawler(crawler, *args, **kwargs)
# #         crawler.signals.connect(spider.spider_idle, signals.spider_idle)
        
#         cls.mongo_uri=crawler.settings.get('MONGO_URI'),
#         cls.mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
#         cls.collection_name = crawler.settings.get("SEBENARNYA_COLLECTION")
#         cls.recrawl_freq = crawler.settings.get("RECRAWL_FREQUENCY")
                
#         cls.mongo_uri=cls.MONGO_URI
#         cls.mongo_db=cls.MONGO_DATABASE
#         cls.collection_name = cls.SEBENARNYA_COLLECTION
#         cls.recrawl_freq = cls.RECRAWL_FREQUENCY
        
#         cls.client = pymongo.MongoClient(cls.mongo_uri)
#         cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
#         return spider
    
#     def parse(self, response):
#         news_links = response.css('div.td-pb-span8 .entry-title a::attr(href)').getall() 
#         news_links_filtered = [j for j in news_links if check_to_scrap(j, self.coll)]
#         yield from response.follow_all(news_links_filtered, self.parse_news)

#         pagination_links = response.css('.page-nav a')

#         if len(pagination_links) == 1:
#             yield from response.follow_all(pagination_links, self.parse)
#             self.pg += 1
#         elif len(pagination_links) == 2:
#             yield from response.follow_all(pagination_links[1:2], self.parse)
#             self.pg += 1

#     def parse_news(self, response):
#         self.num += 1
#         def extract_with_css(query):
#             return response.css(query).get(default='').strip()
        
#         item = {
#             'date': response.css('div.td-post-header time.entry-date::attr(datetime)').get(),
#             'title': extract_with_css('.entry-title::text'),
#             'content_html': response.css('div.td-post-content').getall(),
#             'url': response.url,
#             'label': 'placeholder',
#             'confidence': 'placeholder',
#             'category': 'placeholder',
            
#             'meta_full_html': response.text,
            
#             'dep_content_text': response.css('div.td-post-content p::text').getall(), #deprecated
#             'dep_img_src': response.css('div.td-post-content img::attr(src)').getall() #deprecated

#             }
#         self.coll.insert_one(dict(item))
#         yield {}
        
from my_spider import MySpider

process = CrawlerProcess()
process.crawl(MySpider)
process.start() # the script will block here until all crawling jobs are finished
print("Done")
