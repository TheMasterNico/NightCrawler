# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from pymongo import MongoClient
import scrapy
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
from scrapy.exceptions import DropItem

class NightcrawlerPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['Alkosto']

    def process_item(self, item, spider):
        #valid = True
        #for data in item:
            #if not data:
                #valid = False
                #raise DropItem("Missing {0}!".format(data))
        #if valid:
        #categories = item['category'].split("/")

        self.collection = self.db[item['category']]
        del item['category']
        self.collection.insert_one(dict(item))
        return item
