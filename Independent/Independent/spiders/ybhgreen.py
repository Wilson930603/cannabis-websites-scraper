from Independent.spiders.base_spider import BaseSpider
import scrapy

class ybhGreenSpider(BaseSpider):
    name = 'ybhgreen'
    allowed_domains = ['ybhgreen.ca']
    start_urls = ['https://ybhgreen.ca/?page_id=476']
    p_id = '990047'
    shop_name = 'YBH Green'

    def parse(self, response):
        address = response.xpath('//div[@class="address-text-inner"]/div[@class="content"]/text()').get()
        phone = response.xpath('//div[@class="address-text-inner"]/div[@class="content"]/text()').getall()[-1]
        email = response.xpath('//div[contains(@class, "third")]/div/div[2]/a/@href').get().replace('mailto:', '')
        yield {
			"Producer ID": '',
			"p_id": self.p_id,
			"Producer": self.shop_name,
			"Description": '',
			"Link": 'https://www.ybhgreen.ca',
			"SKU": "",
			"City": 'Oshawa',
			"Province": 'Ontario',
			"Store Name": self.shop_name,
			"Postal Code": 'L1J 2J8',
			"long": '',
			"lat": '',
			"ccc": "",
			"Page Url": 'https://www.ybhgreen.ca/',
			"Active": "Yes",
			"Main image": 'https://ybhgreen.ca/wp-content/uploads/2021/03/logo-2.png',
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
			"Address": '',
			"Additional Info": "",
			"Created": "",
			"Comment": "",
			"Updated": ""
        }
        yield scrapy.Request('https://ybhgreen.ca/?post_type=product', callback=self.parse_products, dont_filter=True)
    
    page_number = 1
    def parse_products(self, response):
        for product in response.xpath('//li[contains(@class, "product type-product")]'):
            url = product.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)
        
        if response.xpath('//a[@class="next page-numbers"]'):
            self.page_number += 1
            yield scrapy.Request(f'https://ybhgreen.ca/?post_type=product&paged={self.page_number}', callback=self.parse_products, dont_filter=True)
    
    def parse_product(self, response):
        print(response.url)
        brand = response.xpath('//div[@class="pwb-single-product-brands pwb-clearfix"]/a/text()').get()
        name = response.xpath('//h1/text()').get()
        category = response.xpath('//div[@class="product_meta"]/span/a/text()').get()
        product_id = response.xpath('//button[@name="add-to-cart"]/@value').get()
        qty = response.xpath('//input[contains(@class, "qty")]/@min').get()
        stock_count = response.xpath('//input[contains(@class, "qty")]/@max').get()
        price =  response.xpath('//p[@class="price"]/span/bdi/text()').get()
        images = response.xpath('//div[@class="woocommerce-product-gallery__image"]/a/@href').getall()
        desc = ' '.join(response.xpath('//div[@id="tab-description"]/p/text()').getall()).replace('\n', '').replace('\xa0', '')
        desc = desc if ':' not in desc or len(desc) < 15 else ''
        type_ = thc = cbd = weight = ''
        for item in response.xpath('//div[@id="tab-description"]/p/text()').getall():
            if 'Type:' in item:
                type_ = item.replace('Type:', '').strip()
            elif 'THC:' in item:
                thc = item.replace('THC:', '').strip()
            elif 'CBD:' in item:
                cbd = item.replace('CBD:', '').strip()
            elif 'g' in item or '"' in item:
                weight = item if item != desc and len(weight) < 15 else ''
        try:
            weight = weight.replace('Size:', '').replace('Variation:', '').replace('CBD', '').strip()
            if 'per' in weight:
                weight = weight.split('per')[-1]
            if ':' in weight:
                weight = ''
        except:
            pass
        
        variation_name = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_variation"]/th/text()').get()
        variation_value = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--attribute_pa_variation"]/td/p/text()').get()

        yield {
            "Page URL": response.url,
            "Brand": brand,
            "Name": name,
            "SKU": '',
            "Out stock status": 'In Stock',
            "Stock count": stock_count,
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": brand,
            "Main image": images[0] if images else '',
            "Description": desc,
            "Product ID": product_id,
            "Additional Information": '',
            "Meta description": "",
            "Meta title": "",
            "Old Price": '',
            "Equivalency Weights": '',
            "Quantity": qty,
            "Weight": weight if len(weight) < 15 else '',
            "Option": variation_name,
            "Option type": '',
            "Option Value": variation_value,
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
            "Attribute 2": 'CBD' if cbd else '',
            "Attribute value 2": cbd if cbd else '',
            "Attribute 3": "Type" if type_ else '',
            "Attribute value 3": type_,
            "Attribute 4": "",
            "Attribute value 4": "",
            "Reviews": '',
            "Review link": "",
            "Rating": '',
            "Address": '',
            "p_id": self.p_id
        }
