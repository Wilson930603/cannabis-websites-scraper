from Independent.spiders.base_spider import BaseSpider
import scrapy


class GatherNGrowScraper(BaseSpider):

    name = 'gatherngrow'
    allowed_domains = ['gatherngrow.ca']
    p_id = '990001'
    shop_name = 'Gather & Grow recreational cannabis'
    headers = {
        "authority": "gatherngrow.ca",
        "cache-control": "max-age=0",
        "sec-ch-ua": '''"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"''',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '''"Windows"''',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q=0.9",
    }
    custom_settings = {'DEFAULT_REQUEST_HEADERS':headers}

    def start_requests(self):
        url = "https://gatherngrow.ca/shop"
        yield scrapy.Request(url, headers=self.headers, callback = self.parse)
        return ''
    
    def parse(self, response):
        img = 'https://gatherngrow.ca' + response.xpath('//div[@class="et_pb_menu__logo"]/a/noscript/img/@src').get()
        contact = response.xpath('//div[@id="mm-2-3"]')
        googleMapsLink = contact.xpath('.//a/@href').get()
        landitude = googleMapsLink.split('ll=')[1].split(',')[0]
        longitude = googleMapsLink.split('ll=')[1].split(',')[1].split('&')[0]
        contact_fields = contact.xpath('.//a/text()').getall()
        phone = contact.xpath('.//a/@href').getall()[-2].replace('tel:', '')

        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": f"{self.shop_name} - Ottawa",
			"Description": "",
			"Link": 'https://gatherngrow.ca',
			"SKU": "",
			"City": "Ottawa",
			"Province": contact_fields[2],
			"Store Name": self.shop_name,
			"Postal Code": contact_fields[2],
			"long": longitude,
			"lat": landitude,
			"ccc": "",
			"Page Url": 'https://gatherngrow.ca/',
			"Active": "",
			"Main image": img,
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '',
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": phone,
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": "",
			"Social": "",
			"FullAddress": contact_fields[0] + ', ' + contact_fields[1],
			"Address": contact_fields[0],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }

        yield scrapy.Request('https://gatherngrow.ca/shop/', callback = self.parse_products, dont_filter=True)


    def parse_products(self, response):
        products = response.xpath('//li[contains(@class, "product")]')
        product_urls = []
        for product in products:
            url = product.xpath('.//a[contains(@class, "woocommerce-LoopProduct-link")]/@href').get()
            product_idx = ''
            for item in product.xpath('@class').get().split(' '):
                if 'post-' in item:
                    product_idx = item.replace('post-', '')
                    break
            product_urls.append(url)
        
        for url in product_urls:
            yield scrapy.Request(url, meta={'URL': url, 'ID': product_idx}, callback = self.parse_details, dont_filter=True)
        
        if len(response.xpath('//a[contains(@class, "next")]')) > 0:
            url = 'https://gatherngrow.ca' + response.xpath('//a[contains(@class, "next")]/@href').get()
            yield scrapy.Request(url, callback = self.parse_products, dont_filter=True)


    def parse_details(self, response):
        title = response.xpath('//div[contains(@class, "et_pb_module et_pb_wc_title")]/div/h1/text()').get()
        try:
            description = response.xpath('//div[contains(@class, "et_pb_module et_pb_wc_description et_pb_wc_description_0_tb_body")]/div/p/text()').get().strip()
        except:
            description = ''
        currency = response.xpath('//p[@class="price"]//text()').getall()[0]
        price = response.xpath('//p[@class="price"]//text()').getall()[1]
        stock = response.xpath('//p[contains(@class, "stock")]/text()').get()
        stock_count = int(stock.replace(' in stock', '')) if 'in stock' in stock else 0
        stock = True if 'in stock' in stock else False
        sku = response.xpath('//span[@class="sku"]/text()').get().split('_')[0]
        weight = ''
        for item in response.xpath('//span[@class="sku"]/text()').get().split('_'):
            if 'g' in item:
                weight = item
        species = brand = thc = cbd = terpene = ''
        information = response.xpath('//div[contains(@class, "et_pb_module et_pb_wc_description et_pb_wc_description_1_tb_body")]/div/p/text()').extract()
        for item in information:
            species = item.replace('Species : ', '').strip() if 'Species' in item else species
            brand = item.replace('Brand : ', '').strip() if 'Brand' in item else brand
            thc = item.replace('THC : ', '').strip() if 'THC' in item else thc
            cbd = item.replace('CBD : ', '').strip() if 'CBD' in item else cbd
            terpene = item.replace('Terpene : ', '').strip() if 'Terpene' in item else terpene

        image = response.xpath('//div[@class="woocommerce-product-gallery__image"]//@src').get()
        try:
            productIDx = response.xpath('//button/@value').get()
        except:
            productIDx = ''
        product_url = response.meta['URL']
        category = response.xpath('//span[@class="posted_in"]/a/text()').get()

        yield {
            'Page URL': product_url,
            'Brand': brand,
            'Name': title,
            'SKU': sku,
            'Out stock status': stock,
            'Stock count': stock_count,
            'Currency': currency,
            'ccc': '',
            'Price': price,
            'Manufacturer': self.shop_name,
            'Main image': image,
            'Description': description,
            'Product ID': productIDx,
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": '0',
            "Equivalency Weights": '',
            "Quantity": "",
            "Weight": weight,
            "Option": "",
            "Option type": '',
            "Option Value": "",
            "Option image": "",
            "Option price prefix": "",
            "Cat tree 1 parent": category,
            "Cat tree 1 level 1": '',
            "Cat tree 1 level 2": "",
            "Cat tree 2 parent": '',
            "Cat tree 2 level 1": "",
            "Cat tree 2 level 2": "",
            "Cat tree 2 level 3": "",
            "Image 2": '',
            "Image 3": '',
            "Image 4": '',
            "Image 5": '',
            "Sort order": "",
            "Attribute 1": 'CBD',
            "Attribute Value 1": cbd,
            "Attribute 2": 'Species',
            "Attribute value 2": species,
            "Attribute 3": "THC",
            "Attribute value 3": thc,
            "Attribute 4": "Terpene",
            "Attribute value 4": terpene,
            "Reviews": '',
            "Review link": "",
            "Rating": '',
            "Address": '',
            "p_id": self.p_id,
        }

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('gatherngrow')
    process.start()
