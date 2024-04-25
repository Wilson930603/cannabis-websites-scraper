import json
import math
import os
import uuid
from typing import Optional
from urllib.parse import urljoin

import scrapy

from Independent.spiders.base_spider import BaseSpider


class ChoomSpider(BaseSpider):
    name = 'choom'
    allowed_domains = ['choom.ca']
    start_urls = ['https://choom.ca/locations']
    stores_guid_file_name = 'choom_stores_guid.json'
    # custom_settings = {'CONCURRENT_REQUESTS': 1}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if os.path.exists(self.stores_guid_file_name):
            with open(self.stores_guid_file_name, 'r', encoding='utf-8') as f:
                self.stores_guid = json.load(f)
        else:
            self.stores_guid = {}

    # def start_requests(self):
    #     yield scrapy.Request('https://choom.ca/vaporizers/vape-cartridge/daily-special-og-kush-vape-cartridge-1-x-05g',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        links = response.xpath('//div[@class="column is-4"]/h2'
                               '/a[@class="is-choomblue"]/@href').extract()
        for link in links:
            url = link.replace('/locations/', '/shop/')
            store_id = link.split('/')[-1]
            if store_id in self.stores_guid:
                p_id = self.stores_guid[store_id]
            else:
                p_id = uuid.uuid4().hex
                self.stores_guid[store_id] = p_id
            yield scrapy.Request(url,
                                 callback=self.parse_shop,
                                 meta={'p_id': p_id})

        with open(self.stores_guid_file_name, 'w', encoding='utf-8') as f:
            json.dump(self.stores_guid, f)

        yield from self.extract_stores(response)

    @staticmethod
    def _extract_choom_session(response):
        cookie = response.headers[b'Set-Cookie'].decode('utf-8').split(';')[0].split('=')
        return cookie[1]

    def parse_shop(self, response):
        p_id = response.meta['p_id']
        choom_session = self._extract_choom_session(response)
        see_all_links = response.xpath('//div[@class="category-products"]/div'
                                       '/a[contains(text(), "All")]/@href').extract()
        for link in see_all_links:
            url = urljoin(self.start_urls[0], link)
            cookie = f'age-gate=yes; preferred_location=1; emailsignup=signupdone; ' \
                     f'choom_session={choom_session}'
            yield scrapy.Request(url,
                                 headers={'Cookie': cookie},
                                 dont_filter=True,
                                 callback=self.parse_product_list,
                                 meta={'cookie': cookie,
                                       'p_id': p_id})

    def parse_product_list(self, response):
        p_id = response.meta['p_id']
        links = response.xpath('//div[@class="box product-box"]'
                               '/div[@class="image"]/a/@href').extract()
        for link in links:
            yield scrapy.Request(link,
                                 dont_filter=True,
                                 callback=self.parse_details,
                                 meta={'p_id': p_id})

        next_page = response.xpath('//nav[@class="pagination"]'
                                   '/a[@class="pagination-next"]/@href').extract_first()
        if next_page:
            cookie = response.meta['cookie']
            yield scrapy.Request(next_page,
                                 headers={'Cookie': cookie},
                                 dont_filter=True,
                                 callback=self.parse_product_list,
                                 meta={'cookie': cookie,
                                       'p_id': p_id})

    def parse_details(self, response):
        indicator = 'window.wkl_product = '
        index1 = response.text.find(indicator)
        if index1 < 0:
            return
        index1 += len(indicator)
        index2 = response.text.find('};', index1)
        wkl_product = response.text[index1: index2 + 1]
        wkl_product = json.loads(wkl_product, strict=False)

        csrf_token = response.xpath('//meta[@name="csrf-token"]/@content').extract_first()
        cookie = f'age-gate=yes; preferred_location={wkl_product["seller_id"]}; emailsignup=signupdone; ' \
                 f'choom_session={self._extract_choom_session(response)}'

        simple_product = response.xpath('//script[@type="application/ld+json"]/text()').extract_first()
        simple_product = json.loads(simple_product)

        images = [x['url'] for x in wkl_product['images']]
        image_count = len(images)

        properties = {}
        trs = response.xpath('//table[@class="table is-bordered is-hoverable"]/tr')
        for tr in trs:
            tds = tr.xpath('td')
            if len(tds) != 2:
                continue
            key = tds[0].xpath('text()').extract_first().strip()
            value = tds[1].xpath('text()').extract_first().replace('\n', '').replace('\t', '').strip()
            properties[key] = value

        thc = ''
        if 'Min THC' in properties:
            thc = properties["Min THC"]
        if 'Max THC' in properties:
            if thc:
                thc = f'{thc} - {properties["Max THC"]}'
            else:
                thc = properties["Max THC"]
        if not thc:
            thc = response.xpath('//div[contains(@class, "product-details")]'
                                 '/p[contains(text(), "THC:")]/text()').extract_first()
            thc = thc.replace('THC:', '').strip() if thc else ''
        cbd = ''
        if 'Min CBD' in properties:
            cbd = properties["Min CBD"]
        if 'Max CBD' in properties:
            if cbd:
                cbd = f'{cbd} - {properties["Max CBD"]}'
            else:
                cbd = properties["Max CBD"]
        if not cbd:
            cbd = response.xpath('//div[contains(@class, "product-details")]'
                                 '/p[contains(text(), "CBD:")]/text()').extract_first()
            cbd = cbd.replace('CBD:', '').strip() if cbd else ''

        review = ''
        if 'aggregateRating' in simple_product and simple_product['aggregateRating']:
            review = simple_product['aggregateRating'].get('reviewCount')
        rating = wkl_product.get('rating')
        stock_status = response.xpath('//div[contains(@class, "status-container")]/p/text()').extract_first()

        item = {
            "Page URL": response.url,
            "Brand": wkl_product['brand']['name'],
            "Name": wkl_product['name'],
            "SKU": wkl_product['sku'],
            "Out stock status": stock_status,
            "Stock count": 0,
            "Currency": "CAD",
            "ccc": "",
            "Price": wkl_product['price_coupon_applied'],
            "Manufacturer": '',
            "Main image": wkl_product['thumb_url'],
            "Description": wkl_product.get('description'),
            "Product ID": wkl_product.get('id'),
            "Additional Information": '',
            "Meta description": wkl_product.get('meta_description'),
            "Meta title": wkl_product.get('meta_title'),
            "Old Price": wkl_product['price'],
            "Equivalency Weights": properties.get('Equivalent To'),
            "Quantity": '',
            "Weight": properties.get('Net Weight'),
            "Option": "",
            "Option type": '',
            "Option Value": '',
            "Option image": "",
            "Option price prefix": '',
            "Cat tree 1 parent": wkl_product.get('category').get('name'),
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
            "Attribute 3": "Strain Classification",
            "Attribute value 3": properties.get('Strain Classification'),
            "Attribute 4": "",
            "Attribute value 4": '',
            "Reviews": review,
            "Review link": f'https://choom.ca/api/products/{wkl_product.get("id")}'
                           f'/reviews?thumb_size=200x200&per_page=20&page=1&sort=newest',
            "Rating": rating if rating and rating > 0 else '',
            "Address": '',
            "p_id": response.meta['p_id']  # wkl_product['seller_id']
        }
        if wkl_product['variants'] and wkl_product['in_stock']:
            for variant in wkl_product['variants']:
                if variant['in_stock']:
                    item['Out stock status'] = 'In stock'
                else:
                    item['Out stock status'] = 'Out of stock'
                if variant['price_coupon_applied']:
                    item['Price'] = variant['price_coupon_applied']
                if variant['price']:
                    item['Old Price'] = variant['price']
                item['Attribute 4'] = 'SKU ID'
                item['Attribute value 4'] = variant['id']
                if variant['options']:
                    option = variant['options'][0]
                    item['Option'] = option['attribute']['name']
                    item['Option type'] = option['attribute']['type']
                    item['Option Value'] = f"{option['value']}{option['attribute']['unit_measure']['symbol']}"
                    item['Option price prefix'] = variant['price'] or item['Price']
                if variant['in_stock']:
                    data = {"id": variant['id'], 'mode': 'add', "qty": "99"}
                    yield from self.query_inventory(cookie, csrf_token, item, data)
                else:
                    yield item
        else:
            if wkl_product['in_stock']:
                data = {"id": wkl_product['id'], 'mode': 'add', "qty": "99"}
                yield from self.query_inventory(cookie, csrf_token, item, data)
            else:
                yield item

    def extract_stores(self, response):
        indicator = 'window.wkl_initial_state.retail_locations = '
        index1 = response.text.find(indicator)
        if index1 < 0:
            return
        index1 += len(indicator)
        index2 = response.text.find('];', index1)
        retail_locations = response.text[index1: index2 + 1]
        retail_locations = json.loads(retail_locations, strict=False)
        for store in retail_locations:
            full_address = f'{store["address"]["address1"]}, ' \
                           f'{store["address"]["city"]}, ' \
                           f'{store["address"]["state"]["name"]} ' \
                           f'{store["address"]["postcode"]} ' \
                           f'{store["address"]["country"]["name"]}'
            item = {"Producer ID": '',
                    "p_id": self.stores_guid[str(store['id'])],
                    "Producer": f'Choom - {store["name"]}',
                    "Description": '',
                    "Link": f'https://choom.ca/shop/{store["id"]}',
                    "SKU": "",
                    "City": store["address"]["city"],
                    "Province": store["address"]["state"]["name"],
                    "Store Name": 'Choom',  # store["name"],
                    "Postal Code": store["address"].get('postcode'),
                    "long": store['coordinates'].get('lng'),
                    "lat": store['coordinates'].get('lat'),
                    "ccc": "",
                    "Page Url": "",
                    "Active": "",
                    "Main image": 'https://choom.ca/images/logo/logo.png',
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Type": "",
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": store.get('phone'),
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": 'customerservice@choom.ca',
                    "Social": {'Facebook': 'https://www.facebook.com/choombrand/',
                               'Instagram': 'https://www.instagram.com/choombrand/',
                               'LinkedIn': 'https://www.linkedin.com/company/choombrand/'},
                    "FullAddress": full_address,
                    "Address": store["address"].get('address1'),
                    "Additional Info": store['open_now'],
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
            yield item

    def query_inventory(self,
                        cookie: str,
                        csrf_token: str,
                        item: dict,
                        data: dict,
                        last_failed: Optional[int] = 0,
                        last_succeed: Optional[int] = 0):
        if 'mode' in data and (last_failed != 0 or last_succeed != 0):
            data.pop('mode')
        headers = {'Accept': 'application/json, text/plain, */*',
                   'Cache-Control': 'no-cache',
                   'Connection': 'keep-alive',
                   'Content-Type': 'application/json;charset=utf-8',
                   'Pragma': 'no-cache',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'cors',
                   'Sec-Fetch-Site': 'same-origin',
                   'X-Requested-With': 'XMLHttpRequest',
                   'X-CSRF-TOKEN': csrf_token,
                   'Cookie': cookie}
        yield scrapy.Request('https://choom.ca/cart',
                             method='POST',
                             headers=headers,
                             body=json.dumps(data),
                             callback=self.parse_add_cart_result,
                             meta={'handle_httpstatus_list': [400, 419, 422],
                                   'cookie': cookie,
                                   'csrf_token': csrf_token,
                                   'item': item,
                                   'data': data,
                                   'last_failed': last_failed,
                                   'last_succeed': last_succeed})

    def parse_add_cart_result(self, response):
        cookie = response.meta['cookie']
        csrf_token = response.meta['csrf_token']
        item = response.meta['item']
        data = response.meta['data']
        old_last_failed = response.meta['last_failed']
        old_last_succeed = response.meta['last_succeed']

        if response.status == 419 or response.status == 422:
            yield item
            return
        elif response.status == 400:
            item["Out stock status"] = response.text
            yield item
            return

        if data['qty'] == 0:
            return

        result = json.loads(response.text)
        result_item = None
        for one in result['items']:
            if one['id'] == data['id']:
                result_item = one
                break

        if result_item.get('error'):
            new_last_failed = int(data['qty'])
            # print(f'Failed Between {old_last_succeed} and {new_last_failed}')
            if math.fabs(old_last_succeed - new_last_failed) == 1:
                item = response.meta['item']
                item["Stock count"] = old_last_succeed
                yield item

                data['qty'] = 0
                yield from self.query_inventory(cookie, csrf_token, item, data, 0, 0)
            else:
                new_quantity = old_last_succeed + math.ceil((new_last_failed - old_last_succeed) / 2)
                data['qty'] = str(new_quantity)
                yield from self.query_inventory(cookie, csrf_token, item, data, new_last_failed, old_last_succeed)
        else:
            new_last_succeed = int(data['qty'])
            # print(f'Succeed Between {new_last_succeed} and {old_last_failed}')
            if math.fabs(old_last_failed - new_last_succeed) == 1:
                item = response.meta['item']
                item["Stock count"] = new_last_succeed
                yield item

                data['qty'] = 0
                yield from self.query_inventory(cookie, csrf_token, item, data, 0, 0)
            else:
                new_quantity = new_last_succeed + math.ceil((old_last_failed - new_last_succeed) / 2)
                data['qty'] = str(new_quantity)
                yield from self.query_inventory(cookie, csrf_token, item, data, old_last_failed, new_last_succeed)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('choom')
    process.start()
