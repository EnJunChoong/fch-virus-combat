# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from .Processing_Sebenarnya import Processing_Sebenarnya


class SplashPipeline(object):
    MONGO_URI = "localhost:27017"
    MONGO_DATABASE = "news"
    COLLECTION = "Standardize1"
    def __init__(self):
        self.client = pymongo.MongoClient(self.MONGO_URI)
        self.coll = self.client[self.MONGO_DATABASE][self.COLLECTION]
    
    
    def process_item(self, item, spider):
        cls = Processing_Sebenarnya(item)
        self.coll.insert_one(cls.json_file)
        return item
    
        

