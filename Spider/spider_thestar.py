import os
import re
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


class TheStarSpider(scrapy.Spider):
    name = "TheStar"
    domain = 'https://www.thestar.com.my'

    MONGO_URI = Settings.MONGO_URI
    MONGO_DATABASE = Settings.MONGO_DB
    THESTAR_COLLECTION_COVID = Settings.THESTAR_RAW_MONGO_COLLECTION
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TheStarSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=cls.MONGO_URI
        cls.mongo_db=cls.MONGO_DATABASE
        cls.collection_name = cls.THESTAR_COLLECTION_COVID
        
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    
    def start_requests(self):     
        urls = [
            'https://www.thestar.com.my/tag/covid-19+watch'
        ]
        
        script = """
            function main(splash, args)
                assert(splash:go(args.url))
                assert(splash:wait(5))   
                while not (splash:select('div[class*=button-view][style*="display: none;"]'))
                    do
                        local loadmore = splash:select('div.button-view.btnLoadMore')
                        loadmore:mouse_click()
                        splash:wait(0.2)
                    end
                return splash:html()
            end
        """
        
        splash_args = {
            'lua_source': script
        }

        for url in urls:
            yield SplashRequest(
                url=url, callback=self.parse_links, 
                endpoint='execute',
                args =splash_args
            )

    
    def parse_links(self, response):
        body = response.css('div.sub-section-list')
        articles = body.css('div.row.list-listing')
        article_links = [article.css('h2.f18').css('a::attr(href)').get() for article in articles]
        article_links = [self.domain+url.replace(self.domain,"") for url in article_links]
        
        print(article_links[:10])
        article_links_filtered = [j for j in article_links if check_to_scrap(j, self.coll)]
        print("Filtered total:")
        print(len(article_links_filtered))
        print(article_links_filtered[:10])
        if len(article_links_filtered) == 0:
            raise CloseSpider 

        # Set to crawl three links only for debugging and setup
        # yield from response.follow_all(article_links[:3], self.parse_news)
        for url in article_links_filtered:
            yield SplashRequest(
                url=url, callback=self.parse_news,
                args = {
                    'wait': 2,
                    'timeout' : 89
                }
            )

    def parse_news(self, response):
        body = response.css('div.articleDetails.focus-wrapper').get()
        #content = body.css('article.story-content').getall()
        #linkname = os.path.basename(response.url)
        #filename = linkname+'.html'
        #title = body.css('div.headline.story-pg').css('h1::text').get()
        #content_html = body.css('article.story-content').getall()
        url = response.url
        # with open('text.html', 'w+') as f:
        #     f.write(date)
        # self.log('Saved file %s' % filename)
        
        
        result_dict = {
            'scrape_date': datetime.datetime.today(),
            'news_date': ,
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
        
        # self.coll.insert_one(result_dict)