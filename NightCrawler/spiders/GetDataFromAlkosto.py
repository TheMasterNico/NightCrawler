import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from NightCrawler.items import AlkostoItem

class GetdatafromalkostoSpider(scrapy.Spider):
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
        url = response.meta.get('url')
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
                item['name'] = prod_url = quote.xpath('./h2[@class="product-name"]/a/@href').get()
                item['old_price'] = old_price = str(quote.xpath('./div[@class="price-box"]/p[@class="old-price"]/span[@class="price-old"]/text()').get()).strip('$\u00a0 \t\n\r').replace('.', '')
                item['new_price'] = new_price = str(quote.xpath('./div[@class="price-box"]/*/*/span[@class="price"]/text()').get()).strip('$\u00a0 \t\n\r').replace('.', '')
                print("  " + title + "::" + prod_name + "[" + new_price + "]::" + prod_url)
                yield item
            next_page_url = response.xpath('//li/a[contains(@class, "next")]/@href').extract_first()
            if next_page_url is not None: #We have Next page
                print("_______________________________________")
                yield response.follow(next_page_url, self.get_data_per_page, meta={'title': title, 'url': category_url})
