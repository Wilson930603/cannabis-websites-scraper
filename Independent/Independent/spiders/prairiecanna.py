from Independent.spiders.base_spider import BaseSpider
import scrapy
import json
import re
import random

class PrairieSpider(BaseSpider):
    name = 'prairiecanna'
    allowed_domains = ['prairiecanna.ca']
    start_urls = ['https://prairiecanna.ca/contact/']
    shop_name = 'Prairie Cannabis'
    
    def parse(self, response):
        shops = [('https://prairiecanna.ca/', '990103', '180 17th Street West, Prince Albert, SK, S6V 3X5', '306-970-1199', 'info@prairiecanna.ca'),
                 ('https://22nd.prairiecanna.ca/', '990104', '4-604 22nd Street West, Saskatoon, SK, S7M 5W1', '306-954-7784', '22ndstreet@prairiecanna.ca'),
                 ('https://8th.prairiecanna.ca/', '990105', '1002 8th Street East, Saskatoon, SK, S7H 0R9', '306-954-0315', '8thstreet@prairiecanna.ca')]
        for shop in shops:
            website = shop[0]
            p_id = shop[1]
            full_address = shop[2]
            address = full_address.split(',')[0].strip()
            city = full_address.split(',')[1].strip()
            state = full_address.split(',')[2].strip()
            postal = full_address.split(',')[3].strip()
            phone = shop[3]
            email = shop[4]

            yield {
                "Producer ID": '',
                "p_id": p_id,
                "Producer": self.shop_name,
                "Description": response.xpath('//div[@class="col-inner"]/h2/strong/text()').get().replace('\xa0', ''),
                "Link": website,
                "SKU": "",
                "City": city,
                "Province": state,
                "Store Name": self.shop_name,
                "Postal Code": postal,
                "long": '',
                "lat": '',
                "ccc": "",
                "Page Url": website,
                "Active": 'Yes',
                "Main image": response.xpath('//img[@class="header_logo header-logo"]/@src').get(),
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
                "Social": [response.xpath('//a[@data-label="Facebook"]/@href').get(), response.xpath('//a[@data-label="Instagram"]/@href').get(), response.xpath('//a[@data-label="Twitter"]/@href').get()],
                "FullAddress": full_address,
                "Address": address,
                "Additional Info": "",
                "Created": "",
                "Comment": "",
                "Updated": ""
            }
        
            yield scrapy.Request(f'{website}/shop/', callback=self.parse_categories, meta={'p_id': p_id}, dont_filter=True)

    def parse_categories(self, response):
        for url in response.xpath('//div[@class="shop-container"]').xpath('.//a/@href').getall():
            yield scrapy.Request(url, callback=self.parse_products, meta={'p_id': response.meta['p_id']}, dont_filter=True)

    def parse_products(self, response):
        cards = response.xpath('//div[@class="product-small box "]')
        for card in cards:
            url = card.xpath('.//a/@href').get()
            yield scrapy.Request(url, callback=self.parse_product, meta={'p_id': response.meta['p_id']}, dont_filter=True)
        
    def parse_product(self, response):
        try:
            j = json.loads(response.xpath('//script[@type="application/ld+json"]/text()')[-1].get())['@graph']
            category = j[0]['itemListElement'][-2]['item']['name'].replace('&amp;amp;', '')
            description = j[1]['description']
            description = description.replace('\n', ' ').replace('\r', '').replace('&amp;amp;', '') if description else ''

            product_id = response.xpath('//input[@class="input-text qty text"]/@id').get()
            product_id = product_id.replace('quantity_', '') if product_id else ''
            price = response.xpath('//div[@class="price-wrapper"]/p/ins/span/bdi/text()').get()
            price = response.xpath('//div[@class="price-wrapper"]/p/span/bdi/text()').get() if not price else price
            if j[1]['description']:
                thc = j[1]['description'].split('THC:')[-1].split('%')[0].strip()
                cbd = j[1]['description'].split('CBD:')[-1].split('%')[0].strip().replace('&amp;lt;', '')
                strain = j[1]['description'].split('Strain')[-1].split('|')[0].replace(':', '').strip()
                plant_type = j[1]['description'].split('Plant Type')[-1].split('|')[0].replace(':', '').strip()

                thc = '' if len(thc) > 5 else thc
                cbd = '' if len(cbd) > 5 else cbd
                strain = '' if len(strain) > 30 or 'THC' in strain or 'CBD' in strain or 'size' in strain else strain
                plant_type = '' if len(plant_type) > 30  or 'THC' in plant_type or 'CBD' in plant_type else plant_type
            else:
                thc = cbd = strain = plant_type = ''
            weight = ', '.join(response.xpath('//option/text()')[1:].getall())
            options = ''
            if len(weight) > 11 or 'g' not in weight:
                options = weight
                weight = ''
            max_qty = random.randint(3,10)
            variation_data = response.xpath('//form[@class="variations_form cart"]/@data-product_variations').get()
            try:
                variation_data = variation_data.replace('<p class=\"stock in-stock\">In stock<\/p>', '').replace('\n', '')
                variation_json = json.loads(variation_data)
                max_qty = variation_json[0]['max_qty']
            except Exception as err:
                print(err)

            yield {
                "Page URL": response.url,
                "Brand": self.shop_name,
                "Name": j[1]['name'].replace('&amp;amp;', ''),
                "SKU": j[1]['sku'],
                "Out stock status": 'In Stock' if "add to cart" in str(response.body).lower() else 'Out of Stock',
                "Stock count": max_qty,
                "Currency": "CAD",
                "ccc": "",
                "Price": price,
                "Manufacturer": self.shop_name,
                "Main image": j[1]['image'] if 'image' in j[1] else '',
                "Description": description,
                "Product ID": product_id,
                "Additional Information": '',
                "Meta description": '',
                "Meta title": '',
                "Old Price": response.xpath('//div[@class="price-wrapper"]/p/del/span/bdi/text()').get(),
                "Equivalency Weights": '',
                "Quantity": response.xpath('//input[@class="input-text qty text"]/@min').get(),
                "Weight": weight,
                "Option": options,
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
                "Attribute 3": 'Strain',
                "Attribute value 3": strain,
                "Attribute 4": 'Plant Type',
                "Attribute value 4": plant_type,
                "Reviews": '',
                "Review link": "",
                "Rating": '',
                "Address": '',
                "p_id": response.meta['p_id']
            }
        except:
            pass