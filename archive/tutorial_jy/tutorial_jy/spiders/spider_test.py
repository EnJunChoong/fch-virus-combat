import scrapy
from scrapy import signals, Request
from scrapy.exceptions import DontCloseSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from .sebenar_spider_v1 import MySpider

class AuthorSpider(scrapy.Spider):
    name = 'author'

    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        author_page_links = response.css('.author + a')
        yield from response.follow_all(author_page_links, self.parse_author)

        pagination_links = response.css('li.next a')
        yield from response.follow_all(pagination_links, self.parse)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }
        
# process = CrawlerProcess(get_project_settings())
process = CrawlerProcess()
process.crawl(AuthorSpider)
process.start() # the script will block here until all crawling jobs are finished
print("Done")
print("Done")
print("Done")