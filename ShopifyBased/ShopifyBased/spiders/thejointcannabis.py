import copy
import json
import math
import time
from typing import Optional
from urllib.parse import urljoin

import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class ThejointCannabisSpider(BaseSpider):
    name = 'thejointcannabis'
    allowed_domains = ['thejointcannabis.ca', 'mybcapps.com']
    start_urls = ['https://thejointcannabis.ca/apps/store-locator']

    # def start_requests(self):
    #     yield scrapy.Request('https://thejointcannabis.ca/products/extracts-inhaled-sk-twd-indica-thc-510-vape-cartridge-format',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        link = response.xpath('//a[@class="main-navigation-parent-link" and contains(text(), "Cannabis")]')
        links = link.xpath('following-sibling::div[1]/ul[@class="mega-menu-list"]/li/ul/li/a/@href').extract()

        locations = []
        containers = response.xpath('//div[@id="addresses_list"]/ul/li/a')
        for one in containers:
            spans = one.xpath('span[@class]')
            store = {}
            for span in spans:
                key = span.xpath('@class').extract_first()
                value = span.xpath('.//text()').extract()
                value = '\n'.join([x.strip() for x in value if x.strip()])
                store[key] = value
            locations.append(store)

        state_stores = {}
        store_json = response.xpath('//script[@id="bms-store-locations"]/text()').extract_first()
        store_json = json.loads(store_json)
        for store in store_json:
            province = store.get('province')
            if province not in state_stores:
                state_stores[province] = [store['shopify_location_id']]
            else:
                state_stores[province].append(store['shopify_location_id'])

            found = False
            store_name = store.get('title')
            phone = postal_zip = ''
            for location in locations:
                if store['city'] != location['city']:
                    continue
                address1 = store['address'].replace('.', '')
                address2 = location['address'].replace('.', '').replace('nd ', ' ')
                if address1 in address2 or address2 in address1:
                    store_name = location.get('name')
                    postal_zip = location.get('postal_zip')
                    phone = location.get('phone')
                    found = True
                    break

            lat = lng = ''
            lat_long = store.get('lat-long')
            if lat_long:
                split_content = lat_long.split(',')
                if len(split_content) >= 2:
                    lat = split_content[0]
                    lng = split_content[1]
                else:
                    self.logger.warning(lat_long)

            item = {"Producer ID": '',
                    "p_id": store['shopify_location_id'],
                    "Producer": f'{store_name} - {store.get("city")} - {store.get("address")}',
                    "Description": '',
                    "Link": '',
                    "SKU": "",
                    "City": store.get('city'),
                    "Province": province,
                    "Store Name": store_name,
                    "Postal Code": postal_zip,
                    "long": lng,
                    "lat": lat,
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
                    "Phone": phone,
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": 'support@thejointcannabis.ca',
                    "Social": "Facebook: https://www.facebook.com/JointHeadShop/, "
                              "Twitter: https://twitter.com/cannabis_joint, "
                              "Instagram: https://instagram.com/thejointcannabis",
                    "FullAddress": f"{store.get('address')} {store.get('city')}, "
                                   f"{store.get('province')} postal_zip, "
                                   f"{store.get('country')}",
                    "Address": store.get('address'),
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
            yield item
            if not found:
                self.logger.warning(store['address'])

        for state, store_ids in state_stores.items():
            for link in links:
                url = urljoin(response.url, f"{link}-{state.lower()}")
                yield scrapy.Request(url,
                                     callback=self.parse_product_list,
                                     meta={'state': copy.copy(state),
                                           'store_ids': copy.copy(store_ids)})
        # yield scrapy.Request('https://thejointcannabis.ca/collections/capsules-ab/',
        #                      callback=self.parse_product_list)

    def parse_product_list(self, response):
        # list_json = response.xpath('//script[@type="application/ld+json" and '
        #                            'contains(text(), "@graph")]/text()').extract_first()
        # list_json = list_json.replace(': ""', ': "').replace('"",', '",').replace('""\n', '"\n')
        # list_json = json.loads(list_json, strict=False)
        # for one in list_json.get('@graph'):
        #     if '@graph' in one:
        #         for two in one.get('@graph'):
        #             if two["@type"] == "Product":
        #                 url = urljoin(response.url, two['url'])
        #                 yield scrapy.Request(url,
        #                                      callback=self.parse_details)
        #                 break

        state = response.meta['state'].lower()
        _st = self._extract_json('var __st=', '};<', response.text)
        if 'rid' not in _st:
            self.logger.warning(_st)
            return
        url_js = f'https://services.mybcapps.com/bc-sf-filter/filter?t={int(time.time()*1000.0)}' \
                 f'&shop=thejointcannabis.myshopify.com&page=1&limit=24&sort=manual&display=grid' \
                 f'&locale=en&collection_scope={_st["rid"]}&product_available=false&variant_available=false' \
                 f'&zero_options=true&build_filter_tree=true&check_cache=true' \
                 f'&pf_t_available[]=available_{state}' \
                 f'&_=pf&pf_st_stock_status[]=true&pf_st_stock_status[]=false' \
                 f'&callback=BCSfFilterCallback&event_type=stock'
        yield scrapy.Request(url_js,
                             headers={'Accept': '*/*'},
                             callback=self.parse_pagination,
                             meta={'rid': copy.copy(_st["rid"]),
                                   'state': state})

    def parse_pagination(self, response):
        brands = self.settings.get('BRANDS', [])
        rid = response.meta['rid']
        state = response.meta['state']

        result = self._extract_json('BCSfFilterCallback(', '});', response.text)
        for product in result['products']:
            # url = f'https://thejointcannabis.ca/collections/flower-ab/products/{product["handle"]}'
            # yield scrapy.Request(url,
            #                      callback=self.parse_details)
            # break
            brand = product.get('vendor')
            if brand and brands and brand not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            title = product.get('title').replace(f'{product["product_type"]} -', '') \
                .replace('- Format:', '').replace('- Grams:', '').replace('- Volume:', '')\
                .replace(f'{state.upper()} -', '').strip()
            if ' - ' in title:
                title = title.split(' - ')[-1]

            images = product.get('images_info', [])
            if images:
                images = [x['src'] for x in images]
            image_count = len(images)

            for variant in product['variants']:
                url = f'https://thejointcannabis.ca/products/{product["handle"]}?variant={variant.get("sku")}'
                # total_inventory = variant.get('inventory_quantity')

                option_name = option_value = ''
                merged_options = variant.get('merged_options')
                if merged_options:
                    merged_options = merged_options[0].split(':')
                    if len(merged_options) == 2:
                        option_name = merged_options[0]
                        option_value = merged_options[1]

                pdp_type = thc = cbd = ''
                for filed in product.get('metafields'):
                    if filed['key'] == 'THC':
                        thc = filed['value']
                    elif filed['key'] == 'CBD':
                        cbd = filed['value']
                    elif filed['key'] == 'TYPE':
                        pdp_type = filed['value']

                inventories = {}
                for field in product.get('variants_metafields_locations'):
                    if field['variantId'] == str(variant['id']):
                        inventories[field['key']] = int(field['value'])

                for shopify_location_id, inventory_count in inventories.items():
                    item = {"Page URL": url,
                            "Brand": brand,
                            "Name": title,
                            "SKU": variant.get("sku"),
                            "Out stock status": 'IN STOCK' if inventory_count > 0 else 'OUT OF STOCK',
                            "Stock count": inventory_count,
                            "Currency": "CAD",
                            "ccc": "",
                            "Price": variant.get('price'),
                            "Manufacturer": product.get('vendor'),
                            "Main image": variant.get('image'),
                            "Description": product.get('body_html'),
                            "Product ID": product.get('id'),
                            "Additional Information": {'SKU ID': variant['id']},
                            "Meta description": "",
                            "Meta title": "",
                            "Old Price": '',
                            "Equivalency Weights": "",
                            "Quantity": '',
                            "Weight": variant.get('title'),
                            "Option": "",
                            "Option type": option_name,
                            "Option Value": option_value,
                            "Option image": "",
                            "Option price prefix": "",
                            "Cat tree 1 parent": product.get('product_type'),
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
                            "Attribute 3": "Product Type",
                            "Attribute value 3": product.get('product_type'),
                            "Attribute 4": "pdp-type",
                            "Attribute value 4": pdp_type,
                            "Reviews": product.get('review_count'),
                            "Review link": "",
                            "Rating": product.get('review_ratings'),
                            "Address": '',
                            "p_id": shopify_location_id}
                    yield item

        current_page = response.meta.get('page', 1)
        if current_page == 1:
            total_pages = math.ceil(result['total_product'] / 24)
            for page in range(2, total_pages + 1):
                url_js = f'https://services.mybcapps.com/bc-sf-filter/filter?t={int(time.time() * 1000.0)}' \
                         f'&shop=thejointcannabis.myshopify.com&page={page}&limit=24&sort=manual&display=grid' \
                         f'&locale=en&collection_scope={rid}&product_available=false&variant_available=false' \
                         f'&zero_options=true&build_filter_tree=true&check_cache=true' \
                         f'&pf_t_available[]=available_{state}' \
                         f'&_=pf&pf_st_stock_status[]=true&pf_st_stock_status[]=false' \
                         f'&callback=BCSfFilterCallback&event_type=stock'
                yield scrapy.Request(url_js,
                                     headers={'Accept': '*/*'},
                                     callback=self.parse_pagination,
                                     meta={'page': page,
                                           'rid': rid,
                                           'state': state})

    def parse_details(self, response):
        product_json = self._extract_json('_SIConfig.product = ', '};', response.text)

        inventory = response.xpath('//script[@class="product-inventory-data"]/text()').extract_first()
        inventory = json.loads(inventory)

        images = product_json.get('media', [])
        if images:
            images = [x['src'] for x in product_json.get('media')]
        image_count = len(images)

        title = response.xpath('//strong[contains(text(), "THC")]')
        if title:
            thc = title.xpath('following-sibling::span[1]/text()').extract_first()
        else:
            thc = ''

        title = response.xpath('//strong[contains(text(), "CBD")]')
        if title:
            cbd = title.xpath('following-sibling::span[1]/text()').extract_first()
        else:
            cbd = ''

        for variant in product_json.get('variants'):
            url = f'{response.url}?variant={variant.get("sku")}'
            inventory_data = inventory.get(variant.get('id'))
            shopify_location_id = inventory_data.keys()[0]
            inventory_count = inventory_data.values()[0]
            if inventory_count < 0:
                inventory_count = 0
            price = variant.get('price')
            featured_image = variant.get('featured_image')
            featured_image = featured_image.get('src') if featured_image else ''
            item = {"Page URL": url,
                    "Brand": variant.get('name'),
                    "Name": product_json.get('title'),
                    "SKU": variant.get("sku"),
                    "Out stock status": 'IN STOCK' if inventory_count > 0 else 'OUT OF STOCK',
                    "Stock count": inventory_count,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": price / 100 if price else '',
                    "Manufacturer": product_json.get('vendor'),
                    "Main image": featured_image,
                    "Description": product_json.get('description'),
                    "Product ID": product_json.get('id'),
                    "Additional Information": None,
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('public_title'),
                    "Option": "",
                    "Option type": product_json.get('options'),
                    "Option Value": variant.get('options'),
                    "Option image": "",
                    "Option price prefix": "",
                    "Cat tree 1 parent": product_json.get('type'),
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
                    "Attribute 3": "Product Type",
                    "Attribute value 3": product_json.get('type'),
                    "Attribute 4": "",
                    "Attribute value 4": "",
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": shopify_location_id}
            yield item

    @staticmethod
    def _extract_json(start_indicator: str, end_indicator: str, html: str) -> Optional[dict]:
        index1 = html.find(start_indicator)
        if index1 < 0:
            return None
        index1 += len(start_indicator)
        index2 = html.find(end_indicator, index1)
        content = html[index1: index2 + 1]
        content = json.loads(content)
        return content


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('thejointcannabis')
    process.start()
