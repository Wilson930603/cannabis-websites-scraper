import abc
import json
import logging
import math
from datetime import datetime
from logging.handlers import RotatingFileHandler

import scrapy


class BaseSpider(scrapy.Spider, abc.ABC):
    allowed_domains = []
    start_urls = ['https://www.leafly.com/dispensary-info/micro-gold-cannabis-okotoks/menu']
    headers = {'accept': 'application/json',
               'content-type': 'application/json',
               'x-app': 'web-dispensary',
               'x-environment': 'production'}

    def __init__(self, city='', **kwargs):
        super().__init__(**kwargs)
        self.city = city.lower().replace("_", " ")

    def _set_crawler(self, crawler):
        super()._set_crawler(crawler)
        if self.settings.get('LOG_ENABLED', False):
            log_file_path = f"{self.settings.get('LOG_FILE_PATH')}" \
                            f"{self.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

            logger = logging.getLogger()
            logger.setLevel(self.settings.get('LOG_LEVEL'))
            formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                                          '%Y-%m-%d %H:%M:%S')
            fhlr = RotatingFileHandler(log_file_path,
                                       maxBytes=50 * 1024 * 1024,
                                       backupCount=5,
                                       encoding='utf-8')
            fhlr.setLevel(self.settings.get('LOG_LEVEL'))
            fhlr.setFormatter(formatter)
            logger.addHandler(fhlr)

    def parse_menu(self, response):
        if response.text.startswith('{'):
            data = json.loads(response.text)
            products = data['data']
            total_count = data['metadata']['totalCount']
        else:
            data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').extract_first()
            if not data:
                self.logger.warning(response.text)
                return

            data = json.loads(data)
            if 'dispensary' not in data['props']['pageProps']:
                self.logger.warning(f'No dispensary: {response.text}')
                return
            producer = data['props']['pageProps']['dispensary']
            if self.city and producer['city'].lower() != self.city:
                self.logger.info(f'Ignore city: {producer["city"]}')
                return

            if 'menuData' not in data['props']['pageProps']:
                self.logger.warning(f'No products {response.url}')
                return
            products = data['props']['pageProps']['menuData']['menuItems']
            total_count = data['props']['pageProps']['menuData']['totalItems']

        if '&skip=' in response.url:
            brands = self.settings.get('BRANDS')
            for product in products:
                store_url = f'https://www.leafly.com/dispensary-info/{product.get("dispensarySlug")}'
                yield scrapy.Request(store_url,
                                     callback=self.parse_store)

                if product['brandName'] and brands and product['brandName'] not in brands:
                    self.logger.debug(f'Ignore brand: {product["brandName"]}')
                    continue

                stock_count = product.get('stockQuantity')
                if stock_count and stock_count > 0:
                    stock_status = 'In Stock'
                else:
                    if stock_count is None:
                        stock_status = 'Call to confirm'
                    else:
                        stock_status = 'Out of Stock'
                image = product.get('imageSet')
                image = image.get('high') if image else ''
                reviews = ''
                rating = ''
                catg = ''
                if product.get('strain'):
                    reviews = product.get('strain').get('reviewCount')
                    rating = product.get('strain').get('averageRating')
                    catg = product.get('strain').get('category')
                item = {"Page URL": f'https://www.leafly.com/dispensary-info/{product.get("dispensarySlug")}/p/{product.get("menuItemId")}/{product.get("id")}',
                        "Brand": product.get('brandName'),
                        "Name": product.get('name'),
                        "SKU": product["id"],
                        "Out stock status": stock_status,
                        "Stock count": stock_count,
                        "Currency": "CAD",
                        "ccc": "",
                        "Price": product.get('price'),
                        "Manufacturer": product.get('dispensaryName'),
                        "Main image": product.get('imageUrl'),
                        "Description": product.get('description'),
                        "Product ID": product["id"],
                        "Additional Information": "",
                        "Meta description": "",
                        "Meta title": "",
                        "Old Price": '',
                        "Equivalency Weights": "",
                        "Quantity": product.get('quantity'),
                        "Weight": product.get('displayQuantity'),
                        "Option": "",
                        "Option type": "",
                        "Option Value": "",
                        "Option image": "",
                        "Option price prefix": "",
                        "Cat tree 1 parent": product.get('productCategory'),
                        "Cat tree 1 level 1": catg,
                        "Cat tree 1 level 2": "",
                        "Cat tree 2 parent": "",
                        "Cat tree 2 level 1": "",
                        "Cat tree 2 level 2": "",
                        "Cat tree 2 level 3": "",
                        "Image 2": image,
                        "Image 3": '',
                        "Image 4": '',
                        "Image 5": '',
                        "Sort order": "",
                        "Attribute 1": "CBD",
                        "Attribute Value 1": product["cbdContent"] if product["cbdUnit"] == "percent" else product["cbdUnit"],
                        "Attribute 2": "THC",
                        "Attribute value 2": product["thcContent"] if product["cbdUnit"] == "percent" else product["thcUnit"],
                        "Attribute 3": "Product Type",
                        "Attribute value 3": product.get('productCategory'),
                        "Attribute 4": "",
                        "Attribute value 4": "",
                        "Reviews": reviews,
                        "Review link": "",
                        "Rating": rating,
                        "Address": '',
                        "p_id": product.get('dispensaryId')}
                yield item

        current_page = response.meta.get('current_page', 0)
        if current_page == 0 and '&skip=' not in response.url:
            total_pages = math.ceil(total_count / 18)
            base_url = response.url
            if base_url.endswith('menu') or base_url.endswith('menu_items'):
                shop_id = base_url.split('/')[-2]
                base_url = f'https://consumer-api.leafly.com/api/dispensaries/v2/{shop_id}/menu_items?take=18&skip=0'
            for index in range(0, total_pages):
                url = base_url.replace('skip=0', f'skip={index * 18}')
                yield scrapy.Request(url,
                                     headers=self.headers,
                                     callback=self.parse_menu,
                                     meta={'current_page': index})

    def parse_store(self, response):
        data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').extract_first()
        if not data:
            self.logger.warning(response.text)
            return

        data = json.loads(data)
        producer = data['props']['pageProps']['dispensary']
        geolocation = data['props']['pageProps']['geolocation']

        photos = producer.get('photos')
        image_count = len(photos) if photos else 0
        item = {"Producer ID": "",
                "p_id": producer['id'],
                "Producer": producer.get('name'),
                "Description": producer.get('description'),
                "Link": producer.get('website', 'https://www.budaboom.com/'),
                "SKU": "",
                "City": geolocation.get('city'),
                "Province": geolocation.get('state'),
                "Store Name": producer.get('name'),
                "Postal Code": geolocation.get('zip'),
                "long": geolocation['coordinates'].get('longitude'),
                "lat": geolocation['coordinates'].get('latitude'),
                "ccc": "",
                "Page Url": response.url,
                "Active": "",
                "Main image": producer.get('coverPhotoUrl'),
                "Image 2": photos[0].get('high') if image_count > 0 else '',
                "Image 3": photos[1].get('high') if image_count > 1 else '',
                "Image 4": photos[2].get('high') if image_count > 2 else '',
                "Image 5": photos[3].get('high') if image_count > 3 else '',
                "Type": producer.get('retailType'),
                "License Type": "",
                "Date Licensed": "",
                "Phone": producer.get('phone'),
                "Phone 2": "",
                "Contact Name": "",
                "EmailPrivate": "",
                "Email": producer.get('email'),
                "Social": "",
                "FullAddress": "",
                "Address": producer.get('address1'),
                "Additional Info": "",
                "Created": producer.get('created'),
                "Comment": "",
                "Updated": producer.get('lastMenuUpdate')}
        yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('leafly')
    process.start()
