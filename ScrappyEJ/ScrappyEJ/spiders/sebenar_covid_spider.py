import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from lxml import html

class SebenarCovidSpider(scrapy.Spider):
    name = "sebenar-covid"
    allowed_domains = ["https://sebenarnya.my/"]

    def start_requests(self):
        urls = [
            'https://sebenarnya.my/category/novel-coronavirus-2019-ncov',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        link = response.url
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        
        
    def parse(self, response):
        articles_page_links = response.css('.author + a')
        yield from response.follow_all(articles_page_links, self.parse_articles)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)

        
        
        
    def parse_articles(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }

    start_urls = ['https://sebenarnya.my/category/novel-coronavirus-2019-ncov/page/20']
    pg = 0
    num = 0
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MySpider, cls).from_crawler(crawler, *args, **kwargs)
        
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