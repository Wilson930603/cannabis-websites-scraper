import copy
import json
import math
from collections import Counter
from typing import Optional

import scrapy

from ShopifyBased.spiders.base_spider import LocationBaseSpider


class ValuebudsSpiderLocation(LocationBaseSpider):
    name = 'valuebuds'
    allowed_domains = []
    start_urls = ['https://valuebuds.com/pages/our-locations']
    base_url = 'https://valuebuds.com'
    website_filter_id = '30500'
    default_email = 'info@valuebuds.com'

    # def start_requests(self):
    #     yield scrapy.Request('https://valuebuds.com/products/rgb-72-volt-s-dried-3-5g?variant=39392022200492',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        # Add "Value Buds - King Street West" manually
        p_id = 'Valuebuds - King West Street'
        store_url = 'https://on.valuebuds.com/pages/search-results-page?collection=value-buds-king-street-west'
        item = {"Producer ID": "",
                "p_id": p_id,
                "Producer": p_id,
                "Description": '',
                "Link": store_url,
                "SKU": "",
                "City": 'Hamilton',
                "Province": 'Ontario',
                "Store Name": p_id,
                "Postal Code": '',
                "long": '',
                "lat": '',
                "ccc": "",
                "Page Url": store_url,
                "Active": "",
                "Main image": '',
                "Image 2": '',
                "Image 3": '',
                "Image 4": '',
                "Image 5": '',
                "Type": "",
                "License Type": "",
                "Date Licensed": "",
                "Phone": '1-855-702-7400',
                "Phone 2": "",
                "Contact Name": "",
                "EmailPrivate": "",
                "Email": 'info@valuebuds.com',
                "Social": "",
                "FullAddress": '',
                "Address": '',
                "Additional Info": "",
                "Created": "",
                "Comment": "",
                "Updated": ""}
        yield item
        self.stores[p_id] = item

        storerocket_id = response.xpath('//div[@id="storerocket-widget"]/@data-storerocket-id').extract_first()
        for province, coord in self.locations.items():
            url = f'https://api.storerocket.io/api/user/{storerocket_id}/locations?' \
                  f'{coord}&radius=2500&filters={self.website_filter_id}'
            yield scrapy.Request(url,
                                 headers={'Accept': 'application/json, text/javascript, */*; q=0.01'},
                                 callback=self.parse_location)

        yield scrapy.Request(store_url,
                             callback=self.parse_store,
                             meta={'store_id': p_id})

    def parse_details(self, response):
        result = response.xpath('//script[@data-product-json]/text()').extract_first()
        result = json.loads(result)
        json_product = result.get('product')
        if not json_product:
            self.logger.warning(result)
            return

        properties = {}
        for one in response.xpath('//div[@class="product_specs"]'
                                  '/div[@class="productattributes"]/text()').extract():
            split = one.strip().split(':')
            if len(split) != 2:
                self.logger.warning(one)
                continue
            properties[split[0].strip()] = split[1].strip()

        brands = self.settings.get('BRANDS', [])
        brand = properties.get('Brand Name')
        if brand and brands and brand not in brands:
            self.logger.debug(f'Ignore brand: {brand}')
            return

        thc = cbd = ''
        containers = response.xpath('//div[@class="product_specs thc_cbd"]'
                                    '/div[@class="productattributes"]')
        for one in containers:
            label = one.xpath('label/@for').extract_first()
            if label == 'ThcRangePercent':
                thc = one.xpath('span/text()').extract_first()
                if thc:
                    thc = thc.replace('\n', '').replace('  ', '').strip()
            elif label == 'CbdRangePercent':
                cbd = one.xpath('span/text()').extract_first()
                if cbd:
                    cbd = cbd.replace('\n', '').replace('  ', '').strip()

        categories = response.xpath('//ol[@class="breadcrumb__list"]'
                                    '/li[@class="breadcrumb__item"]/a/text()').extract()
        category = categories[1].strip() if len(categories) > 1 else ''

        images = [x['src'] for x in json_product['media']] if 'media' in json_product else []
        image_count = len(images)

        product_id = json_product['id']
        variants = json_product.get('variants')
        if not variants:
            self.logger.warning(response.url)
            return
        for variant in variants:
            variant_id = variant['id']
            price = variant.get('price')
            if price is not None:
                try:
                    price = price / 100
                except:
                    self.logger.warning(price)

            item = {"Page URL": f"{response.url}?variant={variant_id}",
                    "Brand": properties.get('Brand Name'),
                    "Name": variant.get('name'),
                    "SKU": variant.get('sku'),
                    "Out stock status": 0,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": price,
                    "Manufacturer": json_product.get('vendor'),
                    "Main image": variant.get('featured_image'),
                    "Description": json_product.get('description'),
                    "Product ID": product_id,
                    "Additional Information": properties,
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('weight'),
                    "Option": "",
                    "Option type": "",
                    "Option Value": "",
                    "Option image": "",
                    "Option price prefix": "",
                    "Cat tree 1 parent": json_product.get('type'),
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": category,
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
                    "Attribute 3": "Product Type",
                    "Attribute value 3": json_product.get('type'),
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant_id,
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": response.meta.get('store_id', '')}

            # yield item
            yield from self.query_inventory_by_location(item,
                                                        str(variant_id),
                                                        str(product_id),
                                                        variant['sku'],
                                                        1,
                                                        {})

    def query_inventory_by_location(self,
                                    item: dict,
                                    variant_id: str,
                                    product_id: str,
                                    sku: str,
                                    quantity: int,
                                    location_inventories: dict,
                                    query_url: str = 'https://api-us.zapiet.com/v1.0/pickup/locations?'
                                                     'shop=vbprod.myshopify.com'):
        form_data = {"shoppingCart[0][variant_id]": variant_id,
                     "shoppingCart[0][product_id]": product_id,
                     "shoppingCart[0][sku]": sku,
                     "shoppingCart[0][quantity]": str(quantity)}
        yield scrapy.FormRequest(query_url,
                                 headers={'Accept': 'application/json, text/javascript, */*; q=0.01',
                                          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                                 formdata=form_data,
                                 callback=self.parse_inventory_by_location,
                                 meta={'item': copy.copy(item),
                                       'variant_id': copy.copy(variant_id),
                                       'product_id': copy.copy(product_id),
                                       'sku': copy.copy(sku),
                                       'quantity': quantity,
                                       'location_inventories': copy.deepcopy(location_inventories)})

    def parse_inventory_by_location(self, response):
        location_inventories = response.meta.get('location_inventories', {})
        results = json.loads(response.text)
        if results['locations']:
            for location in results['locations']:
                if location['id'] in location_inventories:
                    location_inventories[location['id']]['inventory_count'] += 1
                else:
                    location_inventories[location['id']] = {'location': location,
                                                            'inventory_count': 1}

            yield from self.query_inventory_by_location(response.meta['item'],
                                                        response.meta['variant_id'],
                                                        response.meta['product_id'],
                                                        response.meta['sku'],
                                                        response.meta['quantity'] + 1,
                                                        location_inventories)
        else:
            # Done
            if location_inventories:
                for location_id, data_dict in location_inventories.items():
                    item = copy.copy(response.meta['item'])
                    item['Out stock status'] = data_dict['inventory_count']
                    item['p_id'] = self._find_p_id(data_dict['location'])
                    if item['p_id']:
                        yield item
            else:
                yield response.meta['item']

        if results['pagination']['total_pages'] > 1 and \
                results['pagination']['current_page'] < results['pagination']['total_pages']:
            query_url = results['pagination']['next_page_url']
            yield from self.query_inventory_by_location(response.meta['item'],
                                                        response.meta['variant_id'],
                                                        response.meta['product_id'],
                                                        response.meta['sku'],
                                                        response.meta['quantity'] + 1,
                                                        location_inventories,
                                                        query_url)

    def _find_p_id(self, location: dict) -> Optional[int]:
        company_name1 = location['company_name'].replace('ValueBuds', 'Value Buds')
        company_name2 = company_name1.replace(' - ', ' ').replace('  ', ' ')
        for _, store in self.stores.items():
            if company_name2 == 'Value Buds Vermillion' and store["Store Name"] == 'Value Buds Vermilion':
                return store['p_id']
            elif company_name1 == store["Store Name"] or company_name2 == store["Store Name"]:
                return store['p_id']
            else:
                count1 = Counter(company_name2.split())
                count2 = Counter(store["Store Name"].replace('-', '').split())
                if count1 == count2:
                    return store['p_id']
        self.logger.error(f'No store found for location {location}')
        return None

    def query_inventory(self,
                        item: dict,
                        data: dict,
                        last_failed: Optional[int] = 0,
                        last_succeed: Optional[int] = 0):
        yield scrapy.Request('https://valuebuds.com/cart/add.js',
                             method='POST',
                             headers={'accept': '*/*',
                                      'content-type': 'application/json',
                                      'x-requested-with': 'XMLHttpRequest'},
                             body=json.dumps(data),
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
            # Empty cart, just in case
            # yield scrapy.Request('https://valuebuds.com/cart/change.js',
            #                      dont_filter=True,
            #                      method='POST',
            #                      headers={'accept': '*/*',
            #                               'content-type': 'application/json',
            #                               'x-requested-with': 'XMLHttpRequest'},
            #                      body='{"line":"1","quantity":0}',
            #                      callback=self.parse_add_cart_result)

            new_last_succeed = int(data['quantity'])
            # print(f'Succeed Between {new_last_succeed} and {old_last_failed}')
            if math.fabs(old_last_failed - new_last_succeed) == 1:
                item = response.meta['item']
                item["Out stock status"] = new_last_succeed
                yield item
            else:
                new_quantity = new_last_succeed + math.ceil((old_last_failed - new_last_succeed) / 2)
                data['quantity'] = str(new_quantity)
                yield from self.query_inventory(item, data, old_last_failed, new_last_succeed)

    def parse_empty_cart(self, response):
        self.logger.debug(response.text)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('valuebuds')
    process.start()
