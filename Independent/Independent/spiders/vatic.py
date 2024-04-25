from Independent.spiders.base_spider import BaseSpider
import scrapy
import json
import re

class VaticSpider(BaseSpider):
    name = 'vatic'
    allowed_domains = ['vaticco.ca']
    start_urls = ['https://vaticco.ca/contact/']
    shop_name = 'Vatic Cannabis'
    p_id = '990101'
    
    def parse(self, response):
        yield {
            "Producer ID": '',
            "p_id": self.p_id,
            "Producer": self.shop_name,
            "Description": response.xpath('//span[@style="font-size: 75%;"]/text()').get(),
            "Link": 'https://vaticco.ca/',
            "SKU": "",
            "City": 'Emerald Park',
            "Province": 'SK',
            "Store Name": self.shop_name,
            "Postal Code": 'S4L 1B6',
            "long": '31.1908595',
            "lat": '29.9229149',
            "ccc": "",
            "Page Url": response.url,
            "Active": 'Yes',
            "Main image": response.xpath('//img[@class="header-logo-sticky"]/@src').get(),
            "Image 2": "",
            "Image 3": "",
            "Image 4": '',
            "Image 5": '',
            "Type": "",
            "License Type": "",
            "Date Licensed": "",
            "Phone": '306-539-9969',
            "Phone 2": "",
            "Contact Name": "",
            "EmailPrivate": "",
            "Email": 'support@vaticco.ca',
            "Social": "https://www.facebook.com/wiidsk",
            "FullAddress": '40 Great Plains Rd, Emerald Park, SK S4L 1B6, Canada',
            "Address": response.xpath('//p/strong/text()').getall()[1],
            "Additional Info": "",
            "Created": "",
            "Comment": "",
            "Updated": ""
        }
        
        yield scrapy.Request('https://vaticco.ca/shop/', callback=self.parse_products, dont_filter=True)

    def parse_products(self, response):
        cards = response.xpath('//div[@class="product-small box "]')
        for card in cards:
            url = card.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, dont_filter=True)
        
        if cards and len(cards) == 24:
            cur_page = '1' if '/page/' not in response.url else response.url.split('/page/')[-1].replace('/', '')
            page = str(int(cur_page) + 1)
            y = 'https://vaticco.ca/shop/page/' + page
            yield scrapy.Request(y, callback=self.parse_products, dont_filter=True)

        
    def parse_product(self, response):
        j = json.loads(response.xpath('//script[@type="application/ld+json"]/text()')[-1].get())
        description = j['description']
        description = description.replace('\n', ' ').replace('\r', '') if description else ''
        weight = re.findall('[0-9]*x[0-9]*.[0-9]*[a-z]* ', j['name'])
        weight = re.findall('[0-9]x[0-9]*[a-z]* ', j['name']) if not weight else weight
        weight = re.findall('[0-9]x[0-9]*[a-z]*', j['name']) if not weight else weight
        weight = re.findall('[0-9]*g', j['name']) if not weight else weight
        weight = weight[0] if weight and weight[0] != 'g' else ''

        thc = response.xpath('//span[@class="woocommerce-advanced-product-label product-label label-green"]/span/text()').get()
        if thc:
            if 'Seeds' in thc:
                var = 'Seeds'
                thc = thc.replace('Seeds', '')
            elif 'THC' in thc:
                var = 'THC'
                thc = thc.replace('THC', '')
            elif 'CBD' in thc:
                var = 'CBD'
                thc.replace('CBD', '')
            else:
                var = ''
        else:
            var = ''
        product_id = response.xpath('//input[@class="input-text qty text"]/@id').get()
        product_id = product_id.replace('quantity_', '') if product_id else ''
        meta_desc = response.xpath('//meta[@property="og:description"]/@content')
        meta_desc = meta_desc.get().replace('\n', '').replace('\r', '') if meta_desc else ''
        price = response.xpath('//div[@class="price-wrapper"]/p/ins/span/bdi/text()').get()
        price = response.xpath('//div[@class="price-wrapper"]/p/span/bdi/text()').get() if not price else price

        category = response.xpath('//span[@class="posted_in"]/a/text()').getall()[-1]
        c = response.xpath('//span[@class="posted_in"]/a/text()').getall()
        for text in c:
            if 'Grams' in text:
                weight = text.replace('Grams', 'g')
        yield {
            "Page URL": j['url'],
            "Brand": self.shop_name,
            "Name": j['name'],
            "SKU": j['sku'],
            "Out stock status": 'In Stock' if "add to cart" in str(response.body).lower() else 'Out of Stock',
            "Stock count": response.xpath('//input[@class="input-text qty text"]/@max').get(),
            "Currency": "CAD",
            "ccc": "",
            "Price": price,
            "Manufacturer": self.shop_name,
            "Main image": j['image'],
            "Description": description,
            "Product ID": product_id,
            "Additional Information": '',
            "Meta description": meta_desc,
            "Meta title":  response.xpath('//meta[@property="og:title"]/@content').get(),
            "Old Price": response.xpath('//div[@class="price-wrapper"]/p/del/span/bdi/text()').get(),
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
            "Attribute 1": var,
            "Attribute Value 1": thc,
            "Attribute 2": '',
            "Attribute value 2": '',
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