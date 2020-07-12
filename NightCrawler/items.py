# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NightcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class AlkostoItem(scrapy.Item):
    name = scrapy.Field()
    old_price = scrapy.Field()
    new_price = scrapy.Field()
    pass