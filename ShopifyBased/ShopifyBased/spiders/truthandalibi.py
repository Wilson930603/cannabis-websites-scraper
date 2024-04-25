import json
import math
import pathlib
import re
from typing import Optional
from urllib.parse import urljoin

import js2py
import scrapy
from lxml import html
from requests_toolbelt import MultipartEncoder

from ShopifyBased.spiders.base_spider import BaseSpider


class TruthandalibiSpider(BaseSpider):
    name = 'truthandalibi'
    allowed_domains = ['truthandalibi.ca']
    start_urls = ['https://truthandalibi.ca']

    def __init__(self):
        super().__init__()

        path = f'{pathlib.Path(__file__).parent.absolute()}/truthandalibi.js'
        with open(path, 'r') as f:
            self.js = f.read()

    # def start_requests(self):
    #     yield scrapy.Request('https://truthandalibi.ca/products/pink-kush-1',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        links = response.xpath('//ul[@class="navigation__links"]'
                               '/li[@class="navigation__link navigation__entrance-animation"]'
                               '/a/@href').extract()
        for link in links:
            url = urljoin(self.start_urls[0], link)
            yield scrapy.Request(url,
                                 callback=self.parse_list)

        producer = {"Producer ID": '',
                    "p_id": 'truthandalibi.ca',
                    "Producer": 'truthandalibi',
                    "Description": "Truth + Alibi",
                    "Link": 'https://truthandalibi.ca/',
                    "SKU": "",
                    "City": 'Sidney',
                    "Province": 'BC',
                    "Store Name": 'truthandalibi',
                    "Postal Code": 'V8L 1X4',
                    "long": '-123.4020816',
                    "lat": '48.6490782',
                    "ccc": "",
                    "Page Url": "https://truthandalibi.ca/",
                    "Active": "",
                    "Main image": "https://cdn.shopify.com/s/files/1/0583/9529/5917/files"
                                  "/footer_logo_256x256_crop_center.png?v=1625756156",
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Type": "",
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": '778.351.HERB',
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": '',
                    "Social": "",
                    "FullAddress": '2410 Beacon Ave Sidney BC V8L 1X4',
                    "Address": '2410 Beacon Ave Sidney',
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
        yield producer

    def parse_list(self, response):
        brands = self.settings.get('BRANDS', [])
        links = response.xpath('//div[@class="card-list grid"]/div'
                               '/div[contains(@id, "Card")]/a')
        for link in links:
            brand = link.xpath('div/div[@class="card__brand"]/text()').extract_first()
            brand = brand.strip() if brand else ''
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            url = urljoin(self.start_urls[0], link.xpath('@href').extract_first())
            yield scrapy.Request(url,
                                 callback=self.parse_details)

        next_page = response.xpath('//div[@class="pagination"]'
                                   '/a[@class="btn--secondary pagination__btn"]/@href').extract_first()
        if next_page:
            url = urljoin(self.start_urls[0], next_page)
            yield scrapy.Request(url,
                                 callback=self.parse_list)

    def parse_details(self, response):
        json_data = response.xpath('//script[@data-product-json]/text()').extract_first()
        if not json_data:
            return
        json_data = json.loads(json_data)

        description = html.fromstring(json_data.get('description')).text_content()
        cbd = re.search("\d+mg of CBD", description)
        if cbd:
            cbd = cbd[0].replace(' of CBD', '')
        else:
            cbd = ''

        thc = re.search("\d+mg of THC", description)
        if thc:
            thc = thc[0].replace(' of THC', '')
        else:
            thc = ''

        featured_image = json_data.get('featured_image')
        if featured_image and not featured_image.startswith('https'):
            featured_image = f'https:{featured_image}'

        categories = json_data.get('type').split(',')
        categories_count = len(categories)

        images = json_data.get('images')
        if images:
            image_count = len(images)
            images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        else:
            image_count = 0

        tags = json_data.get('tags')

        for variant in json_data['variants']:
            sku_id = variant['id']
            option_value = variant.get('public_title')
            item = {"Page URL": response.url.replace('&view=json', ''),
                    "Brand": json_data.get('vendor'),
                    "Name": variant.get('name'),
                    "SKU": variant.get('sku'),
                    "Out stock status": 'Out of stock',
                    'Stock count': 0,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": variant.get('price') / 100,
                    "Manufacturer": json_data.get('vendor'),
                    "Main image": featured_image,
                    "Description": description,
                    "Product ID": json_data.get('id'),
                    "Additional Information": '',
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('weight') or '',
                    "Option": json_data.get('options')[0] if option_value else '',
                    "Option type": "Select" if option_value else '',
                    "Option Value": option_value,
                    "Option image": variant.get('featured_image'),
                    "Option price prefix": variant.get('price') / 100,
                    "Cat tree 1 parent": categories[0] if categories_count > 0 else '',
                    "Cat tree 1 level 1": categories[1] if categories_count > 1 else '',
                    "Cat tree 1 level 2": categories[2] if categories_count > 2 else '',
                    "Cat tree 2 parent": "",
                    "Cat tree 2 level 1": "",
                    "Cat tree 2 level 2": "",
                    "Cat tree 2 level 3": "",
                    "Image 2": images[0] if image_count > 0 else '',
                    "Image 3": images[1] if image_count > 1 else '',
                    "Image 4": images[2] if image_count > 2 else '',
                    "Image 5": images[3] if image_count > 3 else '',
                    "Sort order": "",
                    "Attribute 1": "CBD" if cbd else '',
                    "Attribute Value 1": cbd,
                    "Attribute 2": "THC" if thc else '',
                    "Attribute value 2": thc,
                    "Attribute 3": "Tags" if tags else '',
                    "Attribute value 3": tags,
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant['id'],
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": 'truthandalibi.ca'}
            event_id = js2py.eval_js(self.js)
            form_data = {'form_type': 'product',
                         'utf8': '✓',
                         # 'Size': variant.get('options')[0],
                         'id': str(sku_id),
                         'quantity': '200',
                         'event_id': event_id}
            yield from self.query_inventory(item, form_data)

    def query_inventory(self,
                        item: dict,
                        data: dict,
                        last_failed: Optional[int] = 0,
                        last_succeed: Optional[int] = 0):
        me = MultipartEncoder(fields=data)
        me_body = me.to_string()
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Content-Type': me.content_type,
                   'X-Requested-With': 'XMLHttpRequest',
                   # 'Content-Length': me.len,
                   'Referrer': item["Page URL"]}
        yield scrapy.Request('https://truthandalibi.ca/cart/add.js',
                             method='POST',
                             headers=headers,
                             body=me_body,
                             callback=self.parse_add_cart_result,
                             meta={'handle_httpstatus_list': [422],
                                   'item': item,
                                   'data': data,
                                   'last_failed': last_failed,
                                   'last_succeed': last_succeed})

    def parse_add_cart_result(self, response):
        item = response.meta['item']
        data = response.meta['data']
        old_last_failed = response.meta['last_failed']
        old_last_succeed = response.meta['last_succeed']
        if response.status == 422:
            new_last_failed = int(data['quantity'])
            # print(f'Failed Between {old_last_succeed} and {new_last_failed}')
            if math.fabs(old_last_succeed - new_last_failed) == 1:
                item = response.meta['item']
                item['Stock count'] = old_last_succeed
                item["Out stock status"] = 'In stock' if old_last_succeed > 0 else 'Out of stock'
                yield item
            else:
                new_quantity = old_last_succeed + math.ceil((new_last_failed - old_last_succeed) / 2)
                data['quantity'] = str(new_quantity)
                yield from self.query_inventory(item, data, new_last_failed, old_last_succeed)
        else:
            new_last_succeed = int(data['quantity'])
            # print(f'Succeed Between {new_last_succeed} and {old_last_failed}')
            if math.fabs(old_last_failed - new_last_succeed) == 1:
                item = response.meta['item']
                item['Stock count'] = new_last_succeed
                item["Out stock status"] = 'In stock' if new_last_succeed > 0 else 'Out of stock'
                yield item
            else:
                new_quantity = new_last_succeed + math.ceil((old_last_failed - new_last_succeed) / 2)
                data['quantity'] = str(new_quantity)
                yield from self.query_inventory(item, data, old_last_failed, new_last_succeed)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('truthandalibi')
    process.start()
