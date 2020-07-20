import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from NightCrawler.items import AlkostoItem
import time 
from pymongo import MongoClient
from scrapy.utils.project import get_project_settings
settings = get_project_settings()

class GetdatafromalkostoSpider(scrapy.Spider):

    def __init__(self, name=None, **kwargs):
        self.start_time = time.time()
        self.dateScraped =  time.time() #time.strftime("%d/%B/%Y - %H:%M:%S GMT%z", time.localtime())
        client = MongoClient(settings['MONGODB_SERVER'], settings['MONGODB_PORT'])
        self.db = client[settings['MONGODB_DB']]
        self.collection = self.db['main_Categories']
        print("Starting crawl at " + time.strftime("%d/%B/%Y - %H:%M:%S GMT%z", time.localtime()))

    def closed(self, response):
        self.ending_time = time.time()
        duration = self.ending_time - self.start_time
        print("Ending crawl with %s seconds" % duration)
    
    name = 'GetDataFromAlkosto'
    allowed_domains = ['alkosto.com']
    start_urls = ['https://www.alkosto.com/']
    custom_settings = { #Custom pipeline for this specific spider
        'ITEM_PIPELINES': {
            'NightCrawler.pipelines.AlkostoPipeline': 300
        }
    }

    def parse(self, response): #start function
        #extract link categories with xpath
        selectores = response.xpath('//div[@class="wrapper2"]/a')
        if selectores:
            for category in selectores:
                link_category = category.xpath('./@href').get()
                title = category.xpath('./h3/text()').get()
                search_in_db = self.collection.find_one({"name": title})  # search if the category is in DB
                if not search_in_db:
                    self.collection.insert_one({"name": title, 'parent': None})  # insert item in DB
                #print("Get new url: " + title)
                yield response.follow(link_category, self.get_data_per_page, meta={'title': title, 'url': link_category, 'parent': title})

    def get_data_per_page(self, response):
        title = response.meta.get('title') #Get the argument category
        parent = response.meta.get('parent')  # Get the parent of the subcategory
        category_url = response.meta.get('url')  # Get the argument category
        
        selectores = response.xpath('//div[@class="subcategories"]/ul/li/a') #Check if the page have categories
        if selectores: #If have categories, we
            #print("Categorias en " + title)
            for category_selector in selectores: #for each category
                category_url = category_selector.xpath('./@href').get()
                subtitle = category_selector.xpath('./@title').get()
                #print("   " + subtitle + "::" + str(parent))
                search_in_db = self.collection.find_one({"name": subtitle})  # search if the category is in DB
                if not search_in_db:
                    self.collection.insert_one({"name": subtitle, 'parent': parent})  # insert item in DB
                # check for more sub categories
                yield response.follow(category_url, self.get_data_per_page, meta={'title': title + '\\' + subtitle, 'url': category_url, 'parent': subtitle})
        else:
            #print("Sarching data in " + title + "(" + url + ")")
            for quote in response.xpath('//ul[contains(@class, "products-grid")]/li[contains(@class, "item")]'): #Para cada h2 con esa clase que se encuentre en la pagina
                item = AlkostoItem()
                prod_name = quote.xpath('./h2[@class="product-name"]/a/@title').get()
                if not prod_name: #If get from "special offers" we can pass to the next prod
                    continue
                item['url'] = quote.xpath('./h2[@class="product-name"]/a/@href').get()
                item['name'] = prod_name
                item['category'] = title
                item['prices'] = {}
                item['prices']['date'] = self.dateScraped
                oldPrice = quote.xpath('./div[@class="price-box"]/p[@class="old-price"]/span[@class="price-old"]/text()').get()
                if oldPrice: #if not oldprice, not store
                    item['prices']['old_price'] = int(str(oldPrice).strip('$\u00a0 \t\n\r').replace('.', ''))
                item['prices']['new_price'] = int(str(quote.xpath('./div[@class="price-box"]/*/*/span[@class="price"]/text()').get()).strip('$\u00a0 \t\n\r').replace('.', ''))
                yield item
            next_page_url = response.xpath('//li/a[contains(@class, "next")]/@href').extract_first()
            if next_page_url is not None: #We have Next page
                #print("_______________________________________")
                yield response.follow(next_page_url, self.get_data_per_page, meta={'title': title, 'url': category_url})

    
#scrapy crawl GetDataFromAlkosto
