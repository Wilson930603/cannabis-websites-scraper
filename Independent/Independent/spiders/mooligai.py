from Independent.spiders.base_spider import BaseSpider
import scrapy
import re

class MooligaiSpider(BaseSpider):
    name = 'mooligai'
    allowed_domains = ['mooligai.ca']
    start_urls = ['https://mooligai.ca/about-us/']
    p_id = '990046'
    shop_name = 'Mooligai'

    def parse(self, response):
        description = ''.join(response.xpath('//div[@class="kc-elm kc-css-50197 kc_text_block"]/p/text()').getall())
        address = response.xpath('//div[@class="footerBox3"]/p/text()').get()
        email = response.xpath('//div[@class="footerBox3"]/a/@href').get().replace('mailto:', '')
        phone = response.xpath('//div[@class="footerBox3"]/a[2]/@href').get().replace('tel:', '')
        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": self.shop_name,
			"Description": description,
			"Link": 'http://www.mooligai.ca',
			"SKU": "",
			"City": address.split(',')[1],
			"Province": 'Ontario',
			"Store Name": self.shop_name,
			"Postal Code": address.split(',')[2].replace('ON', '').strip(),
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'http://www.mooligai.ca/',
			"Active": "Yes",
			"Main image": 'https://mooligai.ca/wp-content/themes/dg-mooligi/assets/images/logo2.png',
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
			"Email": email,
			"Social": "",
			"FullAddress": address,
			"Address": address.split(',')[0],
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }
        yield scrapy.Request('https://mooligai.ca/shop/', callback=self.parse_products, dont_filter=True)
    
    page_number = 1
    def parse_products(self, response):
        for product in response.xpath('//li[contains(@class, "product type-product")]'):
            url = product.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)
        
        if response.xpath('//a[@class="next page-numbers"]'):
            self.page_number += 1
            yield scrapy.Request(f'https://mooligai.ca/shop/?product-page={self.page_number}', callback=self.parse_products, dont_filter=True)
    
    def parse_product(self, response):
        def remove_non_ascii(s):
            return "".join(c for c in s if ord(c)<128)
        brand = response.xpath('//tr[contains(@class, "woocommerce-product-attributes-item--attribute_pa_brand")]/td/p/text()').get()
        name = response.xpath('//h1/text()').get()
        name = remove_non_ascii(name)
        sku = response.xpath('//span[@class="sku"]/text()').get()
        stock = response.xpath('//p[contains(@class, "stock")]/text()').get()
        price =  response.xpath('//span[@class="price"]/span/bdi/text()').get()
        images = response.xpath('//div[@class="woocommerce-product-gallery__image"]/a/@href').getall()
        desc = response.xpath('//div[@id="tab-description"]/p/text()').get().replace('\n', '')
        desc = remove_non_ascii(desc)
        weight = response.xpath('//div[@class="productSize"]/button/text()').get()
        thc =  response.xpath('//div[@class="productSize"]/span/text()').get().strip().split('\n')[-1].strip()
        cbd =  response.xpath('//div[@class="productSize"]/span[2]/text()').get().strip().split('\n')[-1].strip()

        yield {
            "Page URL": response.url,
            "Brand": brand,
            "Name": name,
            "SKU": sku,
            "Out stock status": 'In Stock' if 'in stock' in stock else 'Out of Stock',
            "Stock count": re.findall('\d*', stock)[0],
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": self.shop_name,
            "Main image": images[0],
            "Description": desc,
            "Product ID": '',
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": '',
            "Equivalency Weights": '',
            "Quantity": "",
            "Weight": weight,
            "Option": "",
            "Option type": '',
            "Option Value": "",
            "Option image": "",
            "Option price prefix": "",
            "Cat tree 1 parent": "",
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
            "Attribute 2": 'CBD' if cbd else '',
            "Attribute value 2": cbd if cbd else '',
            "Attribute 3": "",
            "Attribute value 3": '',
            "Attribute 4": "",
            "Attribute value 4": "",
            "Reviews": '',
            "Review link": "",
            "Rating": '',
            "Address": '',
            "p_id": self.p_id
        }
