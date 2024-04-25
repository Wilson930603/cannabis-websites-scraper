import abc
import json
import math
from urllib.parse import quote

import scrapy

from LeaflyBased.spiders.base_spider import BaseSpider


class KeywordSpider(BaseSpider, abc.ABC):
    start_urls = ['https://www.leafly.com/search?q=']
    keyword = ''

    def start_requests(self):
        url = f'https://www.leafly.com/search/shop?q={quote(self.keyword)}&searchCategory=dispensary'
        yield scrapy.Request(url,
                             headers={'cookie': 'leafly-location=%7B%22coordinates%22%3A%7B%22latitude%22%3A51.04473309999999%2C%22longitude%22%3A-114.0718831%2C%22accuracy_radius%22%3A%22%22%2C%22accuracy_radius_units%22%3A%22%22%7D%2C%22street%22%3A%7B%22name%22%3A%22%22%2C%22number%22%3A%22%22%7D%2C%22sublocality%22%3A%22%22%2C%22city%22%3A%22Calgary%22%2C%22state%22%3A%22Alberta%22%2C%22state_code%22%3A%22AB%22%2C%22country%22%3A%22Canada%22%2C%22country_code%22%3A%22CA%22%2C%22zip%22%3A%22%22%2C%22place_id%22%3A%22ChIJ1T-EnwNwcVMROrZStrE7bSY%22%2C%22slug%22%3A%22calgary-ab-ca%22%2C%22formatted_location%22%3A%22Calgary%2C%20AB%22%7D; userMedRecPreference=Rec'})

    def parse(self, response, **kwargs):
        data = response.xpath('//script[@id="__NEXT_DATA__"]/text()').extract_first()
        if not data:
            self.logger.warning(response.text)
            return

        data = json.loads(data)
        if 'dispensary' not in data['props']['initialState']['shop']:
            self.logger.warning(f'No dispensary: {response.text}')
            return

        for producer in data['props']['initialState']['shop']['dispensary']:
            url = f'https://web-dispensary.leafly.com/api/menu/v2/{producer["slug"]}'
            paylaod = {"params": {"skip": 0, "take": 18, "q": self.keyword, "brandPromotedTake": 0},
                       "cancelToken": {"promise": {}}}
            yield scrapy.Request(url,
                                 method='POST',
                                 headers=self.headers,
                                 body=json.dumps(paylaod),
                                 callback=self.parse_menu,
                                 meta={'current_page': 0})

            store_url = f'https://www.leafly.com/dispensary-info/{producer.get("slug")}'
            yield scrapy.Request(store_url,
                                 callback=self.parse_store)

    def parse_menu(self, response):
        data = json.loads(response.text)
        products = data['data']

        brands = self.settings.get('BRANDS')
        for product in products:
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
            item = {
                "Page URL": f'https://www.leafly.com/dispensary-info/{product.get("dispensarySlug")}/p/{product.get("menuItemId")}/{product.get("id")}',
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
        if current_page == 0:
            total_pages = math.ceil(data['metadata']['totalCount'] / 18)
            for index in range(1, total_pages):
                paylaod = {"params": {"skip": index * 18, "take": 18, "q": self.keyword, "brandPromotedTake": 0},
                           "cancelToken": {"promise": {}}}
                yield scrapy.Request(response.url,
                                     method='POST',
                                     headers=self.headers,
                                     body=json.dumps(paylaod),
                                     callback=self.parse_menu,
                                     meta={'current_page': index})


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('keyword')
    process.start()
