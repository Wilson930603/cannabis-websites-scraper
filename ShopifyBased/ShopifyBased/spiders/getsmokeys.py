import html
import json
import math
from typing import Optional
from urllib.parse import urljoin

import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class GetsmokeysSpider(BaseSpider):
    name = 'getsmokeys'
    allowed_domains = ['getsmokeys.com']
    start_urls = ['https://getsmokeys.com']

    # def start_requests(self):
    #     yield scrapy.Request('https://getsmokeys.com/collections/pre-rolls/products/violet-tourist-pink-og-pre-roll',
    #                          callback=self.parse_details)

    def start_requests(self):
        yield scrapy.Request('https://getsmokeys.com/pages/locations')

    def parse(self, response, **kwargs):
        locations_url = response.xpath('//noscript[@class="store-list-url"]/text()').extract_first()
        url = urljoin(self.start_urls[0], locations_url.strip())
        yield scrapy.Request(url,
                             callback=self.parse_locations)

    def parse_locations(self, response):
        store_list = response.xpath('//noscript[@id="store-pickup-list"]/text()').extract()
        store_list = json.loads('\n'.join(store_list), strict=False)
        for store_id, store_data in store_list.items():
            url = f'https://getsmokeys.com/collections/all/Location:{store_id}?page=1&view=json'
            yield scrapy.Request(url,
                                 callback=self.parse_list,
                                 meta={'p_id': store_id})

    def parse_list(self, response):
        p_id = response.meta['p_id']
        brands = self.settings.get('BRANDS', [])
        products = response.json()
        for product in products[0].get('products'):
            brand = product.get('vendor')
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            availability = product.get('variant-availability')
            for variant in product['variants']:
                sku_id = variant.get('id')
                available = False
                if availability:
                    variant_availability = availability.get(str(sku_id))
                    if variant_availability:
                        store = variant_availability['locations'].get(p_id)
                        if store:
                            available = store.get('available')

                url = f'https://getsmokeys.com/products/{product["handle"]}?variant={sku_id}&view=json'
                yield scrapy.Request(url,
                                     callback=self.parse_sku,
                                     meta={'sku_id': int(sku_id),
                                           'available': available,
                                           'option': variant.get('option1'),
                                           'p_id': p_id})

            stores = product.get('store-availability')
            if stores and p_id in stores['locations']:
                store_data = stores['locations'].get(p_id)
                name = html.unescape(store_data.get("name"))
                address = store_data.get('address')
                producer = {"Producer ID": '',
                            "p_id": p_id,
                            "Producer": f'{name} - {address.get("city")}',
                            "Description": '',
                            "Link": '',
                            "SKU": "",
                            "City": address.get('city'),
                            "Province": address.get('province'),
                            "Store Name": name,
                            "Postal Code": address.get('zip'),
                            "long": address.get('longitude'),
                            "lat": address.get('latitude'),
                            "ccc": "",
                            "Page Url": "https://getsmokeys.com/pages/locations",
                            "Active": "",
                            "Main image": "",
                            "Image 2": '',
                            "Image 3": '',
                            "Image 4": '',
                            "Image 5": '',
                            "Type": "",
                            "License Type": "",
                            "Date Licensed": "",
                            "Phone": address.get('phone'),
                            "Phone 2": "",
                            "Contact Name": "",
                            "EmailPrivate": "",
                            "Email": 'high@getsmokeys.com',
                            "Social": "Facebook: https://www.facebook.com/GetSmokeys/, "
                                      "Twitter: https://twitter.com/getsmokeys?lang=en, "
                                      "Instagram: https://www.instagram.com/getsmokeys/",
                            "FullAddress": f"{address.get('address1')} {address.get('city')}, "
                                           f"{address.get('province')} {address.get('zip')}, "
                                           f"{address.get('country_code')}",
                            "Address": address.get('address1'),
                            "Additional Info": "",
                            "Created": "",
                            "Comment": "",
                            "Updated": ""}
                yield producer

    def parse_sku(self, response):
        p_id = response.meta['p_id']
        sku_id = response.meta['sku_id']
        available = response.meta['available']
        option = response.meta['option']

        properties = json.loads(response.text)
        variant = None
        for one in properties['variants']:
            if one['id'] == sku_id:
                variant = one
                break

        main_image = properties.get('featured_image')
        main_image = f'https:{main_image}' if main_image else ''
        images = properties.get('images')
        images = [f'https:{x}' for x in images] if images else []
        image_count = len(images)

        quantity = ''
        weight = ''
        title = variant.get('title')
        if 'x' in title:
            parts = title.split('x')
            if len(parts) == 2:
                quantity = parts[0].strip()
                weight = parts[1].strip()
        elif title.endswith('g'):
            weight = title

        tags_dict = {}
        for tag in properties.get('tags'):
            if ':' in tag:
                parts = tag.split(':')
                tags_dict[parts[0]] = parts[1]
        if 'CBD Content (Min)' in tags_dict:
            cbd = f"{tags_dict['CBD Content (Min)']}-{tags_dict['CBD Content (Max)']}{tags_dict['CBD Content UofM']}"
        else:
            cbd = ''
        if 'THC Content (Min)' in tags_dict:
            thc = f"{tags_dict['THC Content (Min)']}-{tags_dict['THC Content (Max)']}{tags_dict['THC Content UofM']}"
        else:
            thc = ''

        item = {"Page URL": response.url.replace('&view=json', ''),
                "Brand": properties.get('vendor'),
                "Name": variant.get('name'),
                "SKU": variant.get('sku'),
                "Out stock status": 0,
                "Currency": "CAD",
                "ccc": "",
                "Price": variant.get('price') / 100,
                "Manufacturer": properties.get('vendor'),
                "Main image": main_image,
                "Description": properties.get('description'),
                "Product ID": properties.get('id'),
                "Additional Information": properties,
                "Meta description": "",
                "Meta title": "",
                "Old Price": '',
                "Equivalency Weights": "",
                "Quantity": quantity,
                "Weight": weight,
                "Option": option,
                "Option type": "Select",
                "Option Value": variant.get('title'),
                "Option image": "",
                "Option price prefix": variant.get('price') / 100,
                "Cat tree 1 parent": properties.get('type'),
                "Cat tree 1 level 1": '',
                "Cat tree 1 level 2": "",
                "Cat tree 2 parent": "",
                "Cat tree 2 level 1": "",
                "Cat tree 2 level 2": "",
                "Cat tree 2 level 3": "",
                "Image 2": images[1] if image_count > 1 else '',
                "Image 3": images[2] if image_count > 2 else '',
                "Image 4": images[3] if image_count > 3 else '',
                "Image 5": images[4] if image_count > 4 else '',
                "Sort order": "",
                "Attribute 1": "CBD",
                "Attribute Value 1": cbd,
                "Attribute 2": "THC",
                "Attribute value 2": thc,
                "Attribute 3": "",
                "Attribute value 3": '',
                "Attribute 4": "",
                "Attribute value 4": '',
                "Reviews": '',
                "Review link": "",
                "Rating": '',
                "Address": '',
                "p_id": p_id}

        if not available:
            yield item
        else:
            form_data = {'form_type': 'product',
                         'utf8': '✓',
                         'id': str(sku_id),
                         'quantity': '100'}
            yield from self.query_inventory(item, form_data)

    def query_inventory(self,
                        item: dict,
                        data: dict,
                        last_failed: Optional[int] = 0,
                        last_succeed: Optional[int] = 0):
        headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With': 'XMLHttpRequest',
                   'Referrer': item["Page URL"]}
        yield scrapy.FormRequest('https://getsmokeys.com/cart/add.js',
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
                item["Out stock status"] = old_last_succeed
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
                locations = item["Additional Information"]['store-availability'].get('locations')
                for store_id, location in locations.items():
                    if location['available'] == 'true':
                        item["Out stock status"] = new_last_succeed
                    item['p_id'] = store_id
                    yield item

                    address = location.get('address')
                    producer = {"Producer ID": '',
                                "p_id": store_id,
                                "Producer": f'{location.get("name")} - {address.get("city")}',
                                "Description": '',
                                "Link": '',
                                "SKU": "",
                                "City": address.get('city'),
                                "Province": address.get('province'),
                                "Store Name": location.get('name'),
                                "Postal Code": address.get('zip'),
                                "long": address.get('longitude'),
                                "lat": address.get('latitude'),
                                "ccc": "",
                                "Page Url": "",
                                "Active": "",
                                "Main image": "",
                                "Image 2": '',
                                "Image 3": '',
                                "Image 4": '',
                                "Image 5": '',
                                "Type": "",
                                "License Type": "",
                                "Date Licensed": "",
                                "Phone": address.get('phone'),
                                "Phone 2": "",
                                "Contact Name": "",
                                "EmailPrivate": "",
                                "Email": 'high@getsmokeys.com',
                                "Social": "Facebook: https://www.facebook.com/GetSmokeys/, "
                                          "Twitter: https://twitter.com/getsmokeys?lang=en, "
                                          "Instagram: https://www.instagram.com/getsmokeys/",
                                "FullAddress": f"{address.get('address')} {address.get('city')}, "
                                               f"{address.get('province')} {address.get('zip')}, "
                                               f"{address.get('country_code')}",
                                "Address": address.get('address1'),
                                "Additional Info": "",
                                "Created": "",
                                "Comment": "",
                                "Updated": ""}
                    yield producer
            else:
                new_quantity = new_last_succeed + math.ceil((old_last_failed - new_last_succeed) / 2)
                data['quantity'] = str(new_quantity)
                yield from self.query_inventory(item, data, old_last_failed, new_last_succeed)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('getsmokeys')
    process.start()
