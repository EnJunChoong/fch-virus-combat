import scrapy
import re
    
class AuthorSpider(scrapy.Spider):
    name = 'sebenarnya_old'
    start_urls = ['https://sebenarnya.my/category/novel-coronavirus-2019-ncov/']
    pg = 0
    num = 0
    def parse(self, response):
        news_links = response.css('div.td-pb-span8 .entry-title a')
        yield from response.follow_all(news_links, self.parse_news)

        pagination_links = response.css('.page-nav a')

        if self.pg >= 2:
            print("END:", self.pg) # stop going next page
            yield
        else:
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
            'no': self.num,
            'title': extract_with_css('.entry-title::text'),
            'label': 'placeholder',
            'entry-date': response.css('div.td-post-header time.entry-date::attr(datetime)').get(),
            'text': response.css('div.td-post-content p::text').getall(),
            'img_src': response.css('div.td-post-content img::attr(src)').getall(),
            'from_page': self.pg,
            'url': response.url,
            #             'html': response.text
            }

