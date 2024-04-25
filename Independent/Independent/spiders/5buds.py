from Independent.spiders.base_spider import BaseSpider
import scrapy
import json

class BudsSpider(BaseSpider):
    name = '5buds'
    allowed_domains = ['5buds.ca']
    start_urls = ['https://5buds.ca/contact/']
    shop_name = '5 Buds Cannabis'
    p_id = '990111'
    
    def parse(self, response):
        yield {
            "Producer ID": '',
            "p_id": self.p_id,
            "Producer": self.shop_name,
            "Description": '',
            "Link": 'https://5buds.ca/',
            "SKU": "",
            "City": 'Kindersley',
            "Province": 'SK',
            "Store Name": self.shop_name,
            "Postal Code": 'SOL 1SO',
            "long": '',
            "lat": '',
            "ccc": "",
            "Page Url": response.url,
            "Active": 'Yes',
            "Main image": response.xpath('//img[@alt="5Buds Cannabis"]/@src').get(),
            "Image 2": "",
            "Image 3": "",
            "Image 4": '',
            "Image 5": '',
            "Type": "",
            "License Type": "",
            "Date Licensed": "",
            "Phone": '(306) 463-0099',
            "Phone 2": "",
            "Contact Name": "",
            "EmailPrivate": "",
            "Email": '',
            "Social": '',
            "FullAddress": '208 12th Avenue E, Kindersley, SK, S0L 1S0',
            "Address": '208 12th Avenue E',
            "Additional Info": "",
            "Created": "",
            "Comment": "",
            "Updated": ""
        }
        
        yield scrapy.Request('https://5buds.ca/shop/', callback=self.parse_categories, dont_filter=True)

    def parse_categories(self, response):
        for url in response.xpath('//a[@class="product-category"]/@href').getall():
            yield scrapy.Request(url, callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        cards = response.xpath('//div[@class="product-content-loop"]/a/@href').getall()
        for product_url in cards:
            yield scrapy.Request(product_url, callback=self.parse_product, dont_filter=True)

        if cards and len(cards) == 15:
            cur_page = '1' if '/page/' not in response.url else response.url.split('/page/')[-1].replace('/', '')
            page = str(int(cur_page) + 1)
            y = 'https://5buds.ca/product-category/cannabis/page/' + page
            yield scrapy.Request(y, callback=self.parse_products, dont_filter=True)

        
    def parse_product(self, response):
        j = json.loads(response.xpath('//script[@type="application/ld+json"]/text()')[-1].get())
        description = j['description']
        description = description.replace('\n', ' ').replace('\r', '').replace('&amp;amp;', '') if description else ''

        product_id = response.xpath('//input[@class="input-text qty text"]/@id').get()
        product_id = product_id.replace('quantity_', '') if product_id else ''
        price = response.xpath('//p[@class="price"]/ins/span/bdi/text()').get()
        price = response.xpath('//p[@class="price"]/span/bdi/text()').get() if not price else price
        thc = cbd = type = ''
        if j['description']:
            r = j['description'].split('\r')[0].split(' | ')
            if len(r) == 3:
                thc = r[0].split(' ')[-1].replace('&amp;lt;', '')
                cbd = r[1].split(' ')[-1].replace('&amp;lt;', '')
                type = r[2].replace('&amp;lt;', '')
        weight = response.xpath('//tr[@class="woocommerce-product-attributes-item woocommerce-product-attributes-item--weight"]/td/text()').get()
        yield {
            "Page URL": response.url,
            "Brand": self.shop_name,
            "Name": j['name'],
            "SKU": j['sku'],
            "Out stock status": 'In Stock' if "add to cart" in str(response.body).lower() else 'Out of Stock',
            "Stock count": response.xpath('//input[@class="input-text qty text"]/@max').get(),
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": self.shop_name,
            "Main image": j['image'] if 'image' in j else '',
            "Description": description,
            "Product ID": product_id,
            "Additional Information": '',
            "Meta description": '',
            "Meta title": '',
            "Old Price": response.xpath('//div[@class="price-wrapper"]/p/del/span/bdi/text()').get(),
            "Equivalency Weights": '',
            "Quantity": response.xpath('//input[@class="input-text qty text"]/@min').get(),
            "Weight": weight,
            "Option": '',
            "Option type": '',
            "Option Value": "",
            "Option image": "",
            "Option price prefix": "",
            "Cat tree 1 parent": response.xpath('//span[@class="posted_in"]/a/text()').get(),
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
            "Sort order": '',
            "Attribute 1": 'THC',
            "Attribute Value 1": thc,
            "Attribute 2": 'CBD',
            "Attribute value 2": cbd,
            "Attribute 3": 'Other',
            "Attribute value 3": type,
            "Attribute 4": '',
            "Attribute value 4": '',
            "Reviews": '',
            "Review link": "",
            "Rating": '',
            "Address": '',
            "p_id": self.p_id
        }