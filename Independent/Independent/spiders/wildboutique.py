from Independent.spiders.base_spider import BaseSpider
import scrapy
import json

class WildBoutiqueSpider(BaseSpider):
    name = 'wildboutique'
    allowed_domains = ['wiidsk.ca']
    start_urls = ['https://www.wiidsk.ca/contact-us/']
    shop_name = 'Wild Boutique'
    p_id = '990100'
    
    def parse(self, response):
        description = ''.join(response.xpath('//p[@class="has-text-align-left"]//text()').getall())
        yield {
            "Producer ID": '',
            "p_id": self.p_id,
            "Producer": self.shop_name,
            "Description": description.replace('\n', ''),
            "Link": 'https://www.wiidsk.ca/',
            "SKU": "",
            "City": 'Regina',
            "Province": 'Sk',
            "Store Name": self.shop_name,
            "Postal Code": 'S4S 6B4',
            "long": '',
            "lat": '',
            "ccc": "",
            "Page Url": response.url,
            "Active": 'Yes',
            "Main image": response.xpath('//img[@class="custom-logo"]/@src').get(),
            "Image 2": "",
            "Image 3": "",
            "Image 4": '',
            "Image 5": '',
            "Type": "",
            "License Type": "",
            "Date Licensed": "",
            "Phone": '1-306-992-0092',
            "Phone 2": "",
            "Contact Name": "",
            "EmailPrivate": "",
            "Email": '',
            "Social": "https://www.facebook.com/wiidsk",
            "FullAddress": '',
            "Address": response.xpath('//p[@class="has-normal-font-size"]/strong/text()').get(),
            "Additional Info": "",
            "Created": "",
            "Comment": "",
            "Updated": ""
        }
        
        yield scrapy.Request('https://www.wiidsk.ca/shop/', callback=self.parse_categories, dont_filter=True)

    def parse_categories(self, response):
        for category in response.xpath('//ul[@class="products columns-4"]')[0].xpath('.//li'):
            url = category.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        products = response.xpath('//a[@class="woocommerce-LoopProduct-link woocommerce-loop-product__link"]/@href')
        for product in products:
            url = product.get()
            yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)
        if products and len(products) == 16:
            cur_page = '1' if '/page/' not in response.url else response.url.split('/page/')[-1].replace('/', '')
            page = str(int(cur_page) + 1)
            y = response.url.split('/page/')[0] + '/page/' + page
            yield scrapy.Request(y, callback=self.parse_products, dont_filter=True)
    
    def parse_product(self, response):
        j = json.loads(response.xpath('//script[@type="application/ld+json"]/text()')[1].get())
        try:
            j2 = json.loads(response.xpath('//form[@class="variations_form cart"]/@data-product_variations').get())[0]
        except:
            j2 = ''
        category = j['@graph'][0]['itemListElement'][1]['item']['name']
        product = j['@graph'][1]

        if j2:
            thc = j2['variation_description'].split('THC:')[-1].split('%')[0].strip()
            if len(thc) > 8:
                thc = ''
            cbd = j2['variation_description'].split('CBD:')[-1].split('%')[0].strip()
            if len(cbd) > 8:
                cbd = ''
            weight = j2['weight_html']
        else:
            thc = cbd = weight = ''

        yield {
            "Page URL": response.url,
            "Brand": self.shop_name,
            "Name": product['name'],
            "SKU": product['sku'],
            "Out stock status": 'In Stock' if "in stock" in str(response.body).lower() else 'Out of Stock',
            "Stock count": response.xpath('//input[@class="input-text qty text"]/@max').get(),
            "Currency": "CAD",
            "ccc": "",
            "Price": response.xpath('//p[@class="price"]/span/bdi/text()').get(),
            "Manufacturer": self.shop_name,
            "Main image": product['image'] if 'image' in product else '',
            "Description": product['description'].replace('\n', ' ') if product['description'] else '',
            "Product ID": response.xpath('//input[@class="input-text qty text"]/@id').get().replace('quantity_', ''),
            "Additional Information": '',
            "Meta description": response.xpath('//meta[@property="og:description"]/@content').get(),
            "Meta title":  response.xpath('//meta[@property="og:title"]/@content').get(),
            "Old Price": '',
            "Equivalency Weights": '',
            "Quantity": response.xpath('//input[@class="input-text qty text"]/@min').get(),
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
            "Sort order": '',
            "Attribute 1": 'THC',
            "Attribute Value 1": thc,
            "Attribute 2": 'CBD',
            "Attribute value 2": cbd,
            "Attribute 3": '',
            "Attribute value 3": '',
            "Attribute 4": '',
            "Attribute value 4": '',
            "Reviews": '',
            "Review link": "",
            "Rating": '',
            "Address": '',
            "p_id": self.p_id
        }