import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from NightCrawler.items import AlkostoItem
import time

class GetdatafromalkostoSpider(scrapy.Spider):

    def __init__(self, name=None, **kwargs):
        self.start_time = time.time()


    def closed(self, response):
        self.ending_time = time.time()
        duration = self.ending_time - self.start_time
        print("--- %s seconds ---" % duration)
    
    name = 'GetDataFromAlkosto'
    allowed_domains = ['alkosto.com']
    start_urls = ['https://www.alkosto.com/']

    def parse(self, response): #start function
        #extract link categories with xpath
        selectores = response.xpath('//div[@class="wrapper2"]/a')
        if selectores:
            for category in selectores:
                link_category = category.xpath('./@href').get()
                title = category.xpath('./h3/text()').get()
                #print("Get new url: " + title)
                yield response.follow(link_category, self.get_data_per_page, meta={'title': title, 'url': link_category})

    def get_data_per_page(self, response):
        title = response.meta.get('title') #Get the argument category
        category_url = response.meta.get('url')  # Get the argument category
        
        selectores = response.xpath('//div[@class="subcategories"]/ul/li/a') #Check if the page have categories
        if selectores: #If have categories, we
            #print("Categorias en " + title)
            for category_selector in selectores: #for each category
                category_url = category_selector.xpath('./@href').get()
                subtitle = category_selector.xpath('./@title').get()
                #print("   " + title + "::" + category_url)
                # check for more sub categories
                yield response.follow(category_url, self.get_data_per_page, meta={'title': title + '/' + subtitle, 'url': category_url})
        else:
            #print("Sarching data in " + title + "(" + url + ")")
            for quote in response.xpath('//ul[contains(@class, "products-grid")]/li[contains(@class, "item")]'): #Para cada h2 con esa clase que se encuentre en la pagina
                item = AlkostoItem()
                prod_name = quote.xpath('./h2[@class="product-name"]/a/@title').get()
                if not prod_name: #If get from "special offers" we can pass to the next prod
                    continue
                item['url'] = quote.xpath('./h2[@class="product-name"]/a/@href').get()
                item['old_price'] = str(quote.xpath('./div[@class="price-box"]/p[@class="old-price"]/span[@class="price-old"]/text()').get()).strip('$\u00a0 \t\n\r').replace('.', '')
                item['new_price'] = str(quote.xpath('./div[@class="price-box"]/*/*/span[@class="price"]/text()').get()).strip('$\u00a0 \t\n\r').replace('.', '')
                item['name'] = prod_name
                item['category'] = title
                yield item
            next_page_url = response.xpath('//li/a[contains(@class, "next")]/@href').extract_first()
            if next_page_url is not None: #We have Next page
                #print("_______________________________________")
                yield response.follow(next_page_url, self.get_data_per_page, meta={'title': title, 'url': category_url})

    
