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

class AlkostoPipeline:

    def __init__(self):
        client = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        self.db = client[settings['MONGODB_DB']]
        self.collection = self.db['Items']
        self.collection.create_index("url", unique=True)

    def process_item(self, item, spider):
        #category = item['category']
        #categories = category.split("\\")
        #self.collection = self.db[categories[0]]    # The main category    
        #del item['category'] #no store the category
        #self.collection.insert_one(dict(item))
        self.collection.update(
            {
                'url': item['url']
            },{
                '$set': { #Insert this element and then push
                    'url': item['url'],
                    'name': item['name'],
                    'category': item['category']
                },
                '$push': { #push new elements into prices array
                    'prices': {
                        '$each': [
                            item['prices']
                        ],
                        '$position': 0 #Put the data price at first position
                    }
                }
            }, upsert=True)
        return item

############SAVE LIKE THIS: https://docs.mongodb.com/manual/tutorial/model-embedded-one-to-many-relationships-between-documents/
