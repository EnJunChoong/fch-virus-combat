import scrapy
import pymongo
import os
from scrapy_splash import SplashRequest
from scrapy.http.headers import Headers

class MKiniSpider(scrapy.Spider):
    name = "malaysiakini"
    domain = 'https://www.thestar.com.my'
    MONGO_URI = "localhost:27017"
    MONGO_DATABASE = "news"
    THESTAR_COLLECTION = "malaysiakini_v1_test"
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MKiniSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=crawler.settings.get('MONGO_URI'),
        cls.mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        cls.collection_name = crawler.settings.get("THESTAR_COLLECTION")
                
        cls.mongo_uri=cls.MONGO_URI
        cls.mongo_db=cls.MONGO_DATABASE
        cls.collection_name = cls.THESTAR_COLLECTION
        
        cls.client = pymongo.MongoClient(cls.mongo_uri)
        cls.coll = cls.client[cls.mongo_db][cls.collection_name]
        
        return spider
    
    
    def start_requests(self):     
        urls = [
             "https://www.thestar.com.my/tag/covid-19+watch"
        ]
        
        script = """
            function main(splash, args)
                assert(splash:wait(2.5))  
                assert(splash:go(args.url))
                assert(splash:wait(5.5))   
                splash:on_request(function(request)
                    request:set_proxy{
                        host = "120.50.56.137",
                        port = 40553,
                        username = "",
                        password = "",
                        type = "socks4"
                    }
                
                return splash:html()
            end
        """
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
        
        splash_args = {
            'wait':5,
            'lua_source': script,
#             'proxy': "socks4://120.50.56.137:40553"
        }

        for url in urls:
            yield SplashRequest(
                url=url, callback=self.parse_links, 
                endpoint='execute',
                args=splash_args,
                headers = Headers(headers)
            )

    
    def parse_links(self, response):
#         print(response.text)
        
        article_links = response.css('div.news').css('a::attr(href)')
        print("======================")
        print(response.css("div"))
        print(response.css("div.news"))
        print(article_links)
        print("========================")
        raise Exception("STOP")
        # Set to crawl three links only for debugging and setup
        # yield from response.follow_all(article_links[:3], self.parse_news)
#         for url in article_links:
#             yield SplashRequest(
#                 url=self.domain+url, callback=self.parse_news
#             )

    def parse_news(self, response):
        pass
#         body = response.css('div.articleDetails.focus-wrapper')
#         content = body.css('article.story-content').getall()
#         linkname = os.path.basename(response.url)
#         filename = linkname+'.html'
#         date = response.css('p.date::text').get() + response.css('time.timestamp::text').get()
#         title = body.css('div.headline.story-pg').css('h1::text').get().strip()
#         content_html = body.css('article.story-content').getall()
#         url = response.url
#         # with open('text.html', 'w+') as f:
#         #     f.write(date)
#         # self.log('Saved file %s' % filename)
        
#         result_dict = {
#             'date': date,
#             'title': title,
#             'content_html': content_html,
#             'full_html': body,
#             'url': response.url,
#         }
        
#         self.coll.insert_one(result_dict)