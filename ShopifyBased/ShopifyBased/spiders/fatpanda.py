import json
import re
from html import unescape
from urllib.parse import urljoin

import demjson
import scrapy
from scrapy.http import HtmlResponse

from ShopifyBased.spiders.base_spider import BaseSpider


class FatpandaSpider(BaseSpider):
    name = 'fatpanda'
    allowed_domains = ['fatpanda.ca']
    start_urls = ['https://fatpanda.ca']

    # def start_requests(self):
    #     yield scrapy.Request('https://fatpanda.ca/apps/store-locator/',
    #                          callback=self.parse_stores)

    def parse(self, response, **kwargs):
        indicator = 'var shopifyLinkLists = '
        index1 = response.text.find(indicator)
        index1 += len(indicator)
        index2 = response.text.find('];', index1)
        menus = response.text[index1: index2 + 1]
        menus = demjson.decode(menus)
        for one in menus:
            if '-child-' not in one['id'] or one['title'] == "About Us":
                continue

            for entry in one['items']:
                url = urljoin(response.url, entry)
                yield scrapy.Request(url,
                                     callback=self.parse_list)
            #     break
            # break

        yield scrapy.Request('https://fatpanda.ca/apps/store-locator/',
                             callback=self.parse_stores)

    def parse_stores(self, response):
        regx = re.compile('markersCoords.push\(.+\);')
        stores = regx.findall(response.text)
        stores = unescape(stores[0]).replace(');markersCoords.push(', ',') \
            .replace('markersCoords.push(', '[') \
            .replace(');', ']') \
            .replace('\'<', '"<') \
            .replace('\'}', '"}')
        stores = demjson.decode(stores)
        for store in stores:
            address_filed = HtmlResponse(url="", body=store['address'], encoding='utf-8')
            name = address_filed.xpath("//span[@class='name']/text()").extract_first().strip()
            address = address_filed.xpath("//span[@class='address']/text()").extract_first().strip()
            city = address_filed.xpath("//span[@class='city']/text()").extract_first().strip()
            prov_state = address_filed.xpath("//span[@class='prov_state']/text()").extract_first().strip()
            postal_zip = address_filed.xpath("//span[@class='postal_zip']/text()").extract_first().strip()
            full_address = address_filed.xpath('//text()').extract()
            full_address = ' '.join([x.strip() for x in full_address if x.strip()])

            producer = {"Producer ID": '',
                        "p_id": f'fatpanda.ca - {store["id"]}',
                        "Producer": 'fatpanda',
                        "Description": "Based in Winnipeg, Manitoba, Canada, Fat Panda Vape Shop is a premier distributor of vapes, vapour products, e-cigarettes, e-cigs, e-liquid, e-juice and vaping accessories. With retail locations in three provinces and an online store, Fat Panda is Canada's choice for all of your vaping needs!"
                                       "\nWe have a wonderful, friendly and knowledgeable staff. Whether you are a beginner or an expert, our team will provide you with great customer service and guide you to the products that will fit your needs and your budget."
                                       "\nFat Panda has seven vape shops in Winnipeg, three more across southern Manitoba (Selkirk, Gimli and Brandon) and stores in Moose Jaw, Saskatchewan and Thunder Bay, Ontario. Visit us in person or at our webstore, and come Kick-It! with Fat Panda! ",
                        "Link": 'https://fatpanda.ca',
                        "SKU": "",
                        "City": city,
                        "Province": prov_state,
                        "Store Name": name,
                        "Postal Code": postal_zip,
                        "long": store.get('lng'),
                        "lat": store.get('lat'),
                        "ccc": "",
                        "Page Url": "https://fatpanda.ca",
                        "Active": "",
                        "Main image": "https://cdn.shopifycdn.net/s/files/1/1146/8672/files/3TU7p9yD_874x400.png",
                        "Image 2": '',
                        "Image 3": '',
                        "Image 4": '',
                        "Image 5": '',
                        "Type": "",
                        "License Type": "",
                        "Date Licensed": "",
                        "Phone": '1 (844) 748-9329',
                        "Phone 2": "",
                        "Contact Name": "",
                        "EmailPrivate": "",
                        "Email": 'customerservice@fatpanda.ca',
                        "Social": "",
                        "FullAddress": full_address,
                        "Address": address,
                        "Additional Info": "",
                        "Created": "",
                        "Comment": "",
                        "Updated": ""}
            yield producer

    def parse_list(self, response):
        brands = self.settings.get('BRANDS', [])

        containers = response.xpath('//ul[contains(@class, "productgrid--items")]'
                                    '/li//h2[@class="productitem--title"]/a')
        for container in containers:
            name = container.xpath('text()').extract_first()
            if not name:
                continue
            name = name.strip()
            if brands:
                found = False
                for one in brands:
                    if one in name:
                        found = True
                        break
                if not found:
                    self.logger.debug(f'Ignore brand: {name}')
                    return

            link = container.xpath('@href').extract_first()
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_details)

    def parse_details(self, response):
        product_json = response.xpath('//script[@data-section-id="static-product"]/text()').extract_first()
        if not product_json:
            return
        product_json = json.loads(product_json)['product']

        html = HtmlResponse(url="", body=product_json["description"], encoding='utf-8')
        description = '\n'.join([x.strip() for x in html.xpath('//text()').extract() if x.strip()])

        images = product_json.get('images')
        if images:
            image_count = len(images)
            images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        else:
            image_count = 0

        featured_image = product_json.get('featured_image')
        if featured_image and not featured_image.startswith('https'):
            featured_image = f'https:{featured_image}'

        for variant in product_json['variants']:
            product = {"Page URL": f'{response.url}variant?={variant["id"]}',
                       "Brand": product_json.get('vendor'),
                       "Name": variant.get('name'),
                       "SKU": variant.get('sku'),
                       "Out stock status": 'In stock' if variant['available'] else 'Sold out',
                       "Stock count": variant.get('inventory_quantity', 0),
                       "Currency": "CAD",
                       "ccc": "",
                       "Price": variant['price'] / 100,
                       "Manufacturer": product_json.get('vendor'),
                       "Main image": featured_image,
                       "Description": description,
                       "Product ID": product_json['id'],
                       "Additional Information": variant,
                       "Meta description": "",
                       "Meta title": "",
                       "Old Price": variant['compare_at_price'] / 100 if variant['compare_at_price'] else '',
                       "Equivalency Weights": '',
                       "Quantity": '',
                       "Weight": variant.get('weight'),
                       "Option": product_json['options'][0] if product_json['options'] else '',
                       "Option type": 'Select',
                       "Option Value": variant.get('option1'),
                       "Option image": "",
                       "Option price prefix": variant['price'] / 100,
                       "Cat tree 1 parent": product_json.get('type'),
                       "Cat tree 1 level 1": '',
                       "Cat tree 1 level 2": "",
                       "Cat tree 2 parent": '',
                       "Cat tree 2 level 1": "",
                       "Cat tree 2 level 2": "",
                       "Cat tree 2 level 3": "",
                       "Image 2": images[0] if image_count > 0 else '',
                       "Image 3": images[1] if image_count > 1 else '',
                       "Image 4": images[2] if image_count > 2 else '',
                       "Image 5": images[3] if image_count > 3 else '',
                       "Sort order": "",
                       "Attribute 1": "barcode",
                       "Attribute Value 1": variant.get('barcode'),
                       "Attribute 2": "SKU ID",
                       "Attribute value 2": variant['id'],
                       "Attribute 3": "",
                       "Attribute value 3": '',
                       "Attribute 4": "",
                       "Attribute value 4": '',
                       "Reviews": '',
                       "Review link": "",
                       "Rating": '',
                       "Address": '',
                       "p_id": 'fatpanda.ca'}
            yield product


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('fatpanda')
    process.start()
