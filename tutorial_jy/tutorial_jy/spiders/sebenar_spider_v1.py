import scrapy
import pymongo
import logging
import time
from scrapy import signals, Request
from scrapy.exceptions import DontCloseSpider

def check_to_scrap(url, coll):
    x = coll.find_one({'url': url}, { "_id": 1})
    if x is None:
        return True
    else: 
        return False
    
class MySpider(scrapy.Spider):
    name = 'sebenarnya_v1'
    start_urls = ['https://sebenarnya.my/category/novel-coronavirus-2019-ncov/']
    pg = 0
    num = 0
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signals.spider_idle)
        
        cls.mongo_uri=crawler.settings.get('MONGO_URI'),
        cls.mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        cls.collection_name = crawler.settings.get("SEBENARNYA_COLLECTION")
        cls.recrawl_freq = crawler.settings.get("RECRAWL_FREQUENCY")
                
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    def parse(self, response):
        news_links = response.css('div.td-pb-span8 .entry-title a::attr(href)').getall() 
        news_links_filtered = [j for j in news_links if check_to_scrap(j, self.coll)]
        yield from response.follow_all(news_links_filtered, self.parse_news)

        pagination_links = response.css('.page-nav a')

#         if self.pg >= 2:
#             print("END:", self.pg) # stop going next page
#             yield
#         else:
        if len(pagination_links) == 1:
            yield from response.follow_all(pagination_links, self.parse)
            self.pg += 1
        elif len(pagination_links) == 2:
            yield from response.follow_all(pagination_links[1:2], self.parse)
            self.pg += 1

    def parse_news(self, response):
        self.num += 1
        def extract_with_css(query):
            return response.css(query).get(default='').strip()
        
        yield {
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

    def spider_idle(self, spider):
        time.sleep(self.recrawl_freq)
        logging.info('starting a crawl again!')
        self.crawler.engine.schedule(Request(self.start_urls[0], dont_filter=False), spider)
        raise DontCloseSpider