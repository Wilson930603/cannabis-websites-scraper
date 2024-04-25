import json
import math
from typing import Optional
from urllib.parse import urljoin

import scrapy
from scrapy.http import HtmlResponse

from ShopifyBased.spiders.base_spider import BaseSpider


class InterlakereefSpider(BaseSpider):
    name = 'interlakereef'
    allowed_domains = ['interlakereef.com']
    start_urls = ['https://interlakereef.com/collections']

    # def start_requests(self):
    #     yield scrapy.Request('https://interlakereef.com/products/journey-rhino-og-10x0-3g-pre-rolls-indica',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        links = response.xpath('//div[@class="grid grid--no-gutters grid--uniform collection"]'
                               '/div/a/@href').extract()
        for link in links:
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_list)

        producer = {"Producer ID": '',
                    "p_id": 'interlakereef.com',
                    "Producer": 'interlakereef',
                    "Description": "The Interlake Reef is located at 78 Main St Unit C in Riverton, MB. We offer in store shopping, delivery and shipping across Manitoba.",
                    "Link": 'https://interlakereef.com',
                    "SKU": "",
                    "City": 'Riverton',
                    "Province": 'MB',
                    "Store Name": 'Interlake Reef',
                    "Postal Code": '',
                    "long": '',
                    "lat": '',
                    "ccc": "",
                    "Page Url": "https://interlakereef.com",
                    "Active": "",
                    "Main image": "https://cdn.shopifycdn.net/s/files/1/0554/7229/2015/files/B3E22F90-8E47-4A68-97C8-91209381C262_1200x1200.jpg",
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Type": "",
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": '204-378-2896',
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": 'interlakereef@gmail.com',
                    "Social": "https://www.facebook.com/interlakereef",
                    "FullAddress": '78 Main St Unit C, Riverton, MB.',
                    "Address": '78 Main St Unit C',
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
        yield producer

    def parse_list(self, response):
        brands = self.settings.get('BRANDS', [])

        containers = response.xpath('//div[@class="grid grid--no-gutters grid--uniform"]/div/a[@class="product-card"]')
        for container in containers:
            name = container.xpath('div[@class="product-card__info"]'
                                   '/div[@class="product-card__name"]/text()').extract_first()
            if not name:
                continue
            name = name.strip()
            brand = None
            if brands:
                found = False
                for one in brands:
                    if one in name:
                        found = True
                        brand = one
                        break
                if not found:
                    self.logger.debug(f'Ignore brand: {name}')
                    return

            link = container.xpath('@href').extract_first()
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_details,
                                 meta={'brand': brand})

        next_page = response.xpath('//div[@class="pagination"]/span[@class="next"]/a/@href').extract_first()
        if next_page:
            url = urljoin(response.url, next_page)
            yield scrapy.Request(url,
                                 callback=self.parse_list)

    def parse_details(self, response):
        brand = response.meta.get('brand')

        product_json = response.xpath('//script[@id="ProductJson-product-template"]/text()').extract_first()
        if not product_json:
            return
        product_json = json.loads(product_json)

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

        thc = response.xpath('//p[contains(text(), "THC")]//text()').extract()
        if not thc:
            thc = response.xpath('//span[contains(text(), "THC")]//text()').extract()
        thc = ' '.join([x.strip() for x in thc if x.strip()])
        if thc:
            thc = thc.lstrip('THC ')
        cbd = response.xpath('//p[contains(text(), "CBD")]//text()').extract()
        if not cbd:
            cbd = response.xpath('//span[contains(text(), "CBD")]//text()').extract()
        cbd = ' '.join([x.strip() for x in cbd if x.strip()])
        if cbd:
            cbd = cbd.strip().lstrip('CBD ')

        # if len(product_json['variants']) > 1:
        #     print(product_json['variants'])
        for variant in product_json['variants']:
            product = {"Page URL": response.url,
                       "Brand": brand,
                       "Name": variant.get('name'),
                       "SKU": variant.get('sku'),
                       "Out stock status": 'In stock' if variant['available'] else 'Sold out',
                       "Stock count": 0,
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
                       "Option": '',
                       "Option type": '',
                       "Option Value": '',
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
                       "Attribute 1": "CBD",
                       "Attribute Value 1": cbd,
                       "Attribute 2": "THC",
                       "Attribute value 2": thc,
                       "Attribute 3": "barcode",
                       "Attribute value 3": variant.get('barcode'),
                       "Attribute 4": "SKU ID",
                       "Attribute value 4": variant['id'],
                       "Reviews": '',
                       "Review link": "",
                       "Rating": '',
                       "Address": '',
                       "p_id": 'interlakereef.com'}
            if not variant['available']:
                yield product
            else:
                form_data = {'form_type': 'product',
                             'utf8': '✓',
                             'id': str(variant['id']),
                             'quantity': '500'}
                yield from self.query_inventory(product, form_data)

    def query_inventory(self,
                        item: dict,
                        data: dict,
                        last_failed: Optional[int] = 0,
                        last_succeed: Optional[int] = 0):
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referrer': item["Page URL"]}
        yield scrapy.FormRequest('https://interlakereef.com/cart/add.js',
                                 headers=headers,
                                 formdata=data,
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
                item["Out stock status"] = 'In stock' if old_last_succeed > 0 else 'Sold out'
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
                item["Out stock status"] = 'In stock' if new_last_succeed > 0 else 'Sold out'
                yield item
            else:
                new_quantity = new_last_succeed + math.ceil((old_last_failed - new_last_succeed) / 2)
                data['quantity'] = str(new_quantity)
                yield from self.query_inventory(item, data, old_last_failed, new_last_succeed)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('interlakereef')
    process.start()
