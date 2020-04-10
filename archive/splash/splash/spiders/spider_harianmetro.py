import scrapy
import pymongo
import os
import time
from scrapy_splash import SplashRequest

class NewsSpider(scrapy.Spider):
    name = "hmetro"
    domain = 'https://www.hmetro.com.my'
    MONGO_URI = "localhost:27017"
    MONGO_DATABASE = "news"
    HMETRO_COLLECTION_COVID = "hmetro_v1_covid"
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=crawler.settings.get('MONGO_URI'),
        cls.mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        cls.collection_name = crawler.settings.get("HMETRO_COLLECTION_COVID")
                
        cls.mongo_uri=cls.MONGO_URI
        cls.mongo_db=cls.MONGO_DATABASE
        cls.collection_name = cls.HMETRO_COLLECTION_COVID
        
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    
    def start_requests(self):     
        urls = [
            'https://www.hmetro.com.my/search?s=koronavirus'
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_links)    
    
    def parse_links(self, response):
        body = response.css('div.view-content')
        articles = body.css('div.views-field-title')
        article_links = [self.domain+article.css('a::attr(href)').get() 
                         for article in articles
                         if len(article.css('a::attr(href)').get()) > 0
                        ]

        yield from response.follow_all(article_links, self.parse_news)
        
        paginationlink = response.css('li.pager-next a::attr(href)').getall()
 
        if len(paginationlink) > 0:
            page = paginationlink[0][paginationlink[0].find('page'):]
            nextlink = self.domain+'/search?s=koronavirus&'+ page
            print('############\n')
            print(nextlink)
            print('############\n')
            yield from response.follow_all([nextlink], self.parse_links)
            

    def parse_news(self, response):
        time.sleep(1)
        body = response.css('section.col-md-9.col-sm-8').get()
        #content = body.css('article.story-content').getall()
        linkname = os.path.basename(response.url)
        filename = linkname+'.html'
        #title = body.css('div.headline.story-pg').css('h1::text').get()
        #content_html = body.css('article.story-content').getall()
        url = response.url        
        
#         with open('text.html', 'w+') as f:
#             f.write(body)
#         self.log('Saved file %s' % filename)
        
        result_dict = {
#             'title': title,
#             'content_html': content_html,
            'full_html': body,
            'url': response.url,
        }
        
        self.coll.insert_one(result_dict)