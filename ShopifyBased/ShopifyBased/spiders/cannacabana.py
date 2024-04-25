import json
from urllib.parse import urljoin

import demjson
import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class CannacabanaSpider(BaseSpider):
    name = 'cannacabana'
    allowed_domains = ['cannacabana.com', 'shopify.com', 'warely.io']
    start_urls = ['https://cannacabana.com/']

    # def start_requests(self):
    #     yield scrapy.Request('https://cannacabana.com/products/pure-sunfarms-pink-kush?variant=40006076563644',
    #                          callback=self.parse_details,
    #                          meta={'store_id': '3413'})
    #     yield scrapy.Request('https://cdn.cannacabana.com/cache/collections/all-3413.html',
    #                          callback=self.parse_product_list,
    #                          meta={'store_id': '3413'})

    def parse(self, response, **kwargs):
        stores_js = response.xpath('//script[contains(@src, "stores.js")]/@src').extract_first()
        stores_js = f'https:{stores_js}' if not stores_js.startswith('http') else stores_js
        yield scrapy.Request(stores_js,
                             headers={'accept': '*/*'},
                             callback=self.parse_stores_js)

    def parse_stores_js(self, response):
        content = response.text.split('//#')[0]
        content = content[:-2].replace('window.stores=', '').replace('!0', '0')
        content = demjson.decode(content)
        store_ids = []
        for store_slug, store_data in content.items():
            store_id = store_data.get('store_id', '')
            if store_id:
                store_ids.append(store_id)

            main_image = store_data.get('img')
            if main_image:
                main_image = f"https://cannacabana.imgix.net/stores/photos/{main_image}"
            else:
                main_image = 'https://cdn.shopifycdn.net/s/files/1/0520/7713/4012/t/2/assets/cannacabana-logo-color.svg'

            address = store_data['address']
            producer = {"Producer ID": '',
                        "p_id": store_id,
                        "Producer": f"CANNA Cabana - {store_data['title']}",
                        "Description": '',
                        "Link": store_data['shop_url'],
                        "SKU": "",
                        "City": address['city'],
                        "Province": address['province'],
                        "Store Name": store_data['title'],
                        "Postal Code": address['zip'],
                        "long": address['longitude'],
                        "lat": address['latitude'],
                        "ccc": "",
                        "Page Url": store_data['shop_url'],
                        "Active": "",
                        "Main image": main_image,
                        "Image 2": '',
                        "Image 3": '',
                        "Image 4": '',
                        "Image 5": '',
                        "Type": "",
                        "License Type": "",
                        "Date Licensed": "",
                        "Phone": store_data['phone'],
                        "Phone 2": "",
                        "Contact Name": "",
                        "EmailPrivate": "",
                        "Email": store_data['email'],
                        "Social": "Facebook: https://www.facebook.com/cannacabanacanada, "
                                  "Instagram: https://www.instagram.com/canna.cabana",
                        "FullAddress": f"{address['street1']} {address['province']} {address['city']} "
                                       f"{address['zip']} {address['country']}",
                        "Address": address['street1'],
                        "Additional Info": "",
                        "Created": "",
                        "Comment": "",
                        "Updated": ""}
            yield producer

        yield scrapy.Request('https://cannacabana.com/collections/shop-by-brand',
                             callback=self.parse_brand_list,
                             meta={'store_ids': store_ids})

    def parse_brand_list(self, response):
        links = response.xpath('//div[@class="brand col-3_xs-6"]/p/a/@href').extract()
        for link in links:
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_brand_products,
                                 meta={'store_ids': response.meta['store_ids']})

    def parse_brand_products(self, response):
        indicator = '"CategoryID": "'
        index1 = response.text.find(indicator)
        if index1 < 0:
            return
        index1 += len(indicator)
        index2 = response.text.find('",', index1)
        category_id = response.text[index1: index2]

        for store_id in response.meta['store_ids']:
            url = f'https://warely.io/cannacabana/get-collection?' \
                  f'id={category_id}&store={store_id}&customer=false&page=1'
            yield scrapy.Request(url,
                                 callback=self.parse_product_list,
                                 meta={'store_id': store_id})

    def parse_product_list(self, response):
        store_id = response.meta.get('store_id')

        brands = self.settings.get('BRANDS', [])
        containers = response.xpath('//div[@class="grid-middle-noBottom"]/div/div[contains(@class, "content")]')
        for container in containers:
            brand = container.xpath('a/span[@class="vendor"]/text()').extract()
            brand = brand[-1].replace('•', '').strip() if brand else ''
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            product_url = container.xpath('a/@href').extract_first()
            product_url = urljoin(self.start_urls[0], product_url)
            yield scrapy.Request(product_url,
                                 dont_filter=True,
                                 callback=self.parse_details,
                                 meta={'store_id': store_id})

        if response.url.endswith('&page=1'):
            links = response.xpath('//ul[@class="pagination"]/li[@class="pagination__page"]'
                                   '/a[@data-to-page]/@href').extract()
            base_url = response.url.split('&page=')[0]
            for link in links:
                url = f'{base_url}{link.replace("?", "&")}'
                yield scrapy.Request(url,
                                     dont_filter=True,
                                     callback=self.parse_product_list,
                                     meta={'store_id': store_id})

    def parse_details(self, response):
        store_id = response.meta.get('store_id')

        variant_inventories = {}
        index1 = index2 = 0
        while True:
            indicator = 'var variant_meta = '
            index1 = response.text.find(indicator, index2)
            if index1 < 0:
                break
            index1 += len(indicator)
            index2 = response.text.find('};', index1)
            variant_meta = response.text[index1: index2 + 1]
            variant_meta = json.loads(variant_meta)
            if store_id not in variant_meta:
                continue

            parts = variant_meta[store_id].split(',')

            indicator = 'window.jane_variants[store_id]["'
            index1 = response.text.find(indicator, index2) + len(indicator)
            index2 = response.text.find('"] = obj;', index1)
            variant_id = response.text[index1: index2]
            variant_inventories[variant_id] = {'inventory_quantity': int(parts[0]),
                                               'price': float(parts[1]),
                                               'compare_at_price': float(parts[2]),
                                               'size': parts[3],
                                               'thc': float(parts[4]),
                                               'cbd': float(parts[5])}
        if not variant_inventories:
            return

        static_product = response.xpath('//script[@data-section-id="static-product"]/text()').extract_first()
        static_product = json.loads(static_product)
        static_product = static_product['product']

        product_json = response.xpath('//script[@type="application/ld+json" and '
                                      'contains(text(), "description")]/text()').extract_first()
        product_json = demjson.decode(product_json)

        images = static_product['images']
        images = [f'https:{x}' if not x.startswith('http') else x for x in images]
        image_count = len(images)

        category = ''
        brand_subtype = ''
        for tag in static_product.get('tags', []):
            if 'brand_subtype' in tag:
                brand_subtype = tag.replace('brand_subtype:', '')
            elif 'lineage' in tag:
                brand_subtype = tag.replace('lineage:', '')
            elif 'category' in tag:
                category = tag.replace('category:', '')

        rating = product_json.get('aggregateRating')
        if rating:
            review_count = rating.get('reviewCount')
            rating_value = '{:0.1f}'.format(float(rating.get('ratingValue')))
        else:
            rating_value = ''
            review_count = ''

        variant_count = len(static_product['variants'])
        for variant in static_product['variants']:
            variant_id = variant['id']
            variant_inventory = variant_inventories.get(str(variant_id), {})
            stock_count = variant_inventory.get('inventory_quantity', 0)

            item = {"Page URL": response.url,
                    "Brand": product_json.get('brand').get('name'),
                    "Name": product_json.get('name') if variant_count == 1 else variant.get('name'),
                    "SKU": f"{variant.get('sku')}_{variant.get('title')}",
                    "Out stock status": 'In Stock' if stock_count else 'Out of Stock',
                    "Stock count": stock_count,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": variant_inventory.get('price'),
                    "Manufacturer": static_product.get('vendor'),
                    "Main image": product_json.get('image', ''),
                    "Description": product_json.get('description').replace('<p>', '').replace('</p>', ''),
                    "Product ID": static_product['id'],
                    "Additional Information": '',
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": variant_inventory.get('compare_at_price'),
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('weight') if variant.get('weight') else '',
                    "Option": "",
                    "Option type": 'List' if variant_count > 0 else '',
                    "Option Value": variant.get('option1') if variant_count > 0 else '',
                    "Option image": variant.get('featured_image') if variant_count > 0 else '',
                    "Option price prefix": variant_inventory.get('price') if variant_count > 0 else '',
                    "Cat tree 1 parent": category,
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": brand_subtype,
                    "Cat tree 2 level 1": "",
                    "Cat tree 2 level 2": "",
                    "Cat tree 2 level 3": "",
                    "Image 2": images[0] if image_count > 0 else '',
                    "Image 3": images[1] if image_count > 1 else '',
                    "Image 4": images[2] if image_count > 2 else '',
                    "Image 5": images[3] if image_count > 3 else '',
                    "Sort order": "",
                    "Attribute 1": "CBD",
                    "Attribute Value 1": variant_inventory.get('cbd') if variant_inventory.get('cbd') else '',
                    "Attribute 2": "THC",
                    "Attribute value 2": variant_inventory.get('thc') if variant_inventory.get('thc') else '',
                    "Attribute 3": "SKU ID",
                    "Attribute value 3": variant_id,
                    "Attribute 4": "",
                    "Attribute value 4": '',
                    "Reviews": review_count,
                    "Review link": response.url,
                    "Rating": rating_value,
                    "Address": '',
                    "p_id": store_id}
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('cannacabana')
    process.start()
