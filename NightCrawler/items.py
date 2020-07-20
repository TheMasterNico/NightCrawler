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
    url = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    prices = scrapy.Field() # This item is array that containts prices and time when is scraped
    #old_price = scrapy.Field()
    #new_price = scrapy.Field()
    #date = scrapy.Field()
    pass
