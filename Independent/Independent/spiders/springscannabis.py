from Independent.spiders.base_spider import BaseSpider
import scrapy
import re

class ybhGreenSpider(BaseSpider):
    name = 'springscannabis'
    allowed_domains = ['shoplightspeed.com']
    start_urls = ['https://springs.shoplightspeed.com/service/locations/']
    p_id = '990049'
    shop_name = 'Springs Cannabis'

    def parse(self, response):
        description = response.xpath('//span[@class="contact-description"]/text()').get()
        address = ', '.join(response.xpath('//p/text()').getall()[:-1])
        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": self.shop_name,
			"Description": description,
			"Link": 'https://springs.shoplightspeed.com',
			"SKU": "",
			"City": address.split(',')[2].strip(),
			"Province": address.split(',')[3],
			"Store Name": self.shop_name,
			"Postal Code": address.split(',')[4],
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://springs.shoplightspeed.com/',
			"Active": "Yes",
			"Main image": response.xpath('//img[@alt="Springs Cannabis"]/@src').get(),
			"Image 2": "",
			"Image 3": "",
			"Image 4": '',
			"Image 5": '', 
			"Type": "",
			"License Type": "",
			"Date Licensed": "",
			"Phone": response.xpath('//div[@class="contact"]/text()').getall()[1].strip(),
			"Phone 2": "",
			"Contact Name": "",
			"EmailPrivate": "",
			"Email": 'orders@springscannabis.ca',
			"Social": "",
			"FullAddress": address,
			"Address": ', '.join(address.split(',')[0:2]),
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }
        categories = response.xpath('//li[contains(@class, "item")]')
        for category in categories:
            url = category.xpath('.//a/@href').get()
            name = category.xpath('.//a/text()').get().strip()
            if len(url.split('/')) == 5 and url != 'https://springs.shoplightspeed.com/':
                yield scrapy.Request(url, meta={'category': name, 'url': url},callback=self.parse_products, dont_filter=True)
    
    def parse_products(self, response):
        for product in response.xpath('//div[contains(@class, "product col-xs-6")]'):
            url = product.xpath('.//a/@href').get()
            yield scrapy.Request(url, meta={'category': response.meta['category']}, callback=self.parse_product, dont_filter=True)
        
        next_page = response.xpath('//li[@class="next enabled"]/a/@href').get()
        if next_page and '/page' in next_page:
            yield scrapy.Request(next_page, meta={'category': response.meta['category'], 'url': response.meta['url']}, callback=self.parse_products, dont_filter=True)
    
    def parse_product(self, response):
        def remove_non_ascii(s):
            return "".join(c for c in s if ord(c)<128)
        name = remove_non_ascii(response.xpath('//h1/text()').get().strip())
        product_id = response.xpath('//form[@id="product_configure_form"]/@action').get().split('/')[-2]
        category = response.meta['category']
        qty = response.xpath('//input[@name="quantity"]/@value').get()
        stock = response.xpath('//tr[@class="availability"]/td[2]/span/text()').get()
        price =  response.xpath('//span[@class="price"]/text()').get().strip().replace('C$', '')
        try:
            oldprice = response.xpath('//div[@class="price-wrap col-xs-5 col-md-5"]/span[@class="old-price"]/text()').get().replace('C$', '')
        except:
            oldprice = ''
        images = response.xpath('//div[@class="thumbs row"]/div/a/img/@src').getall()
        for item in images:
            item = item.replace('156x230x1', '1600x2048x1')
        # desc = response.xpath('//meta[@itemprop="description"]/@content').get()
        desc2 = ' '.join(response.xpath('//div[@class="page info active"]/p/text()').getall())
        desc = remove_non_ascii(desc2)
        try:
            thc = re.findall('[0-9]*.[0-9]*[%]', name)[0] if 'THC' in name else ''
        except:
            thc = ''
        try:
            skuNweight = response.xpath('//meta[@itemprop="mpn"]/@content').get().split('_')
        except:
            skuNweight = ['', '']
        while len(skuNweight) < 2:
            skuNweight.append('')
        brand = response.xpath('//meta[@itemprop="brand"]/@content').get()

        try:
            sku = skuNweight[0]
            int(sku)
        except:
            sku = ''
        
        yield {
            "Page URL": response.url,
            "Brand": brand,
            "Name": name,
            "SKU": sku,
            "Out stock status": stock,
            "Stock count": '',
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": self.shop_name,
            "Main image": images[0],
            "Description": desc,
            "Product ID": product_id,
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": oldprice,
            "Equivalency Weights": '',
            "Quantity": qty,
            "Weight": skuNweight[1],
            "Option": "",
            "Option type": '',
            "Option Value": "",
            "Option image": "",
            "Option price prefix": "",
            "Cat tree 1 parent": category,
            "Cat tree 1 level 1": "",
            "Cat tree 1 level 2": "",
            "Cat tree 2 parent": '',
            "Cat tree 2 level 1": "",
            "Cat tree 2 level 2": "",
            "Cat tree 2 level 3": "",
            "Image 2": images[1] if len(images) > 1 else '',
            "Image 3": images[2] if len(images) > 2 else '',
            "Image 4": images[3] if len(images) > 3 else '',
            "Image 5": images[4] if len(images) > 4 else '',
            "Sort order": "",
            "Attribute 1": 'THC' if thc else '',
            "Attribute Value 1": thc if thc else '',
            "Attribute 2": '',
            "Attribute value 2": '',
            "Attribute 3": '',
            "Attribute value 3": '',
            "Attribute 4": "",
            "Attribute value 4": "",
            "Reviews": '',
            "Review link": "",
            "Rating": '',
            "Address": '',
            "p_id": self.p_id
        }
