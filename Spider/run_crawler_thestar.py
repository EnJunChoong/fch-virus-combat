import scrapy
import scrapy_splash
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet.task import deferLater

from settings import Settings
from spider_thestar import TheStarSpider

def crash(failure):
    print('oops, spider crashed')
    print(failure.getTraceback())
    
def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)

def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print('waiting {} seconds before restart...'.format(wait_time)))
    deferred.addErrback(crash)  # <-- add errback here
    deferred.addCallback(sleep, seconds=wait_time) # wait 10 minutes
    deferred.addCallback(_crawl, spider)
    return deferred


settings = {
                'LOG_LEVEL' :'INFO',
                'SPLASH_URL': 'http://localhost:8050',
                'DOWNLOADER_MIDDLEWARES' : {
                    'scrapy_splash.SplashCookiesMiddleware': 723,
                    'scrapy_splash.SplashMiddleware': 725,
                    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
                },
                'SPIDER_MIDDLEWARES': {
                    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
                },
                'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
                'ROBOTSTXT_OBEY': True,
            }

process = CrawlerProcess(settings)
wait_time = Settings.GENERAL_CRAWL_WAIT_TIME 

_crawl(None, TheStarSpider) # Infinite crawl
process.start()

