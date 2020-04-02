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