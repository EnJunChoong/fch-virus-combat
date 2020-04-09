import scrapy
from scrapy.crawler import CrawlerProcess
from spider_malaysiakini import MKiniSpider

from twisted.internet import reactor
from twisted.internet.task import deferLater

def crash(failure):
    print('oops, spider crashed')
    print(failure.getTraceback())
    
def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)

process = CrawlerProcess()
wait_time = 60*10

def _crawl(result, spider):
    deferred = process.crawl(spider)
    deferred.addCallback(lambda results: print('waiting {} seconds before restart...'.format(wait_time)))
    deferred.addErrback(crash)  # <-- add errback here
    deferred.addCallback(sleep, seconds=wait_time) # wait 10 minutes
    deferred.addCallback(_crawl, spider)
    return deferred

_crawl(None, MKiniSpider) # Infinite crawl
process.start()

