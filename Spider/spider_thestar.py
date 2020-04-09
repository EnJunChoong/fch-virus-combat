import scrapy
import pymongo
import os
from scrapy_splash import SplashRequest

class NewsSpider(scrapy.Spider):
    name = "splash"
    domain = 'https://www.thestar.com.my'
    MONGO_URI = "localhost:27017"
    MONGO_DATABASE = "news"
    THESTAR_COLLECTION_COVID = "thestar_v1_covid"
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        cls.mongo_uri=crawler.settings.get('MONGO_URI'),
        cls.mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        cls.collection_name = crawler.settings.get("THESTAR_COLLECTION_COVID")
                
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
                assert(splash:wait(01))   
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

        # Set to crawl three links only for debugging and setup
        # yield from response.follow_all(article_links[:3], self.parse_news)
        for url in article_links:
            yield SplashRequest(
                url=self.domain+url, callback=self.parse_news,
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
            # 'title': title,
            # 'content_html': content_html,
            'full_html': body,
            'url': response.url,
        }
        
        self.coll.insert_one(result_dict)