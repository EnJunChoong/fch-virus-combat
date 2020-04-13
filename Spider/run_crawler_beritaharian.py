import scrapy
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor
from twisted.internet.task import deferLater

from settings import Settings
from spider_beritaharian import BeritaHarianSpider

def crash(failure):
    print('oops, spider crashed')
    print(failure.getTraceback())
    
def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)

process = CrawlerProcess()
wait_time = Settings.GENERAL_CRAWL_WAIT_TIME 

def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print('waiting {} seconds before restart...'.format(wait_time)))
    deferred.addErrback(crash)  # <-- add errback here
    deferred.addCallback(sleep, seconds=wait_time) # wait 10 minutes
    deferred.addCallback(_crawl, spider)
    return deferred

_crawl(None, BeritaHarianSpider) # Infinite crawl
process.start()

