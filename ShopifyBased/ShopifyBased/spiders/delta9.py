import json
from urllib.parse import urljoin

import scrapy
from scrapy.http import HtmlResponse

from ShopifyBased.spiders.base_spider import BaseSpider


class Delta9Spider(BaseSpider):
    name = 'delta9'
    allowed_domains = ['delta9.ca', 'delta9connect.com', 'stockist.co']
    start_urls = ['https://www.delta9.ca/pages/store-locator']

    # def start_requests(self):
    #     yield scrapy.Request('https://fatpanda.ca/apps/store-locator/',
    #                          callback=self.parse_stores)

    def parse(self, response, **kwargs):
        data_stockist_widget_tag = response.xpath('//div[@data-stockist-widget-tag]'
                                                  '/@data-stockist-widget-tag').extract_first()
        url = f'https://stockist.co/api/v1/{data_stockist_widget_tag}/locations/all.js' \
              f'?callback=_stockistAllStoresCallback'
        yield scrapy.Request(url,
                             callback=self.parse_stores)
        # links = response.xpath('//div/p/a[contains(@href, "/store-locations/")]/@href').extract()
        # for link in links:
        #     url = urljoin(response.url, link)
        #     yield scrapy.Request(url,
        #                          callback=self.parse_store)

    def parse_store(self, response):
        container = response.xpath('//div[@class="panel-container"]/div[@data-zoomlvl]')
        lat = container.xpath('@data-deflat').extract_first()
        lng = container.xpath('@data-deflang').extract_first()

        container = response.xpath('//div[@class="data-item"]')
        name = container.xpath('@data-name').extract_first()
        phone = container.xpath('@data-tel').extract_first()
        email = container.xpath('@data-email').extract_first()
        full_address = container.xpath('@data-address').extract_first()

        parts = full_address.split(',')
        address = parts.pop(0).strip() if parts else ''
        city = parts.pop(0).strip() if parts else ''
        state = parts.pop(0).strip() if parts else ''

        p_id = f'delta9 - {name}'
        producer = {"Producer ID": '',
                    "p_id": p_id,
                    "Producer": 'delta9',
                    "Description": "Delta 9 Cannabis Store is a chain of recreational Cannabis stores in Manitoba, Alberta, and Saskatchewan. Order Marijuana for same day delivery in Winnipeg or shop in our retail stores. Delta 9 Cannabis is also a large Licensed Producer of Marijuana. We are listed on the TSX under the stock ticker DN.",
                    "Link": 'https://www.delta9.ca',
                    "SKU": "",
                    "City": city,
                    "Province": state,
                    "Store Name": name,
                    "Postal Code": '',
                    "long": lng,
                    "lat": lat,
                    "ccc": "",
                    "Page Url": response.url,
                    "Active": "",
                    "Main image": "hhttps://cdn.shopifycdn.net/s/files/1/0090/6438/2521/files/D9C_white-logo_transparent-bg_602x338.png",
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
                    "Email": email,
                    "Social": "",
                    "FullAddress": full_address,
                    "Address": address,
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
        yield producer

        link = container.xpath('div[@class="location-details"]'
                               '//a[contains(text(), "Inventory")]/@href').extract_first()
        url = urljoin(response.url, link)
        yield scrapy.Request(url,
                             callback=self.parse_store_inventory,
                             meta={'p_id': p_id})

    def parse_stores(self, response):
        content = response.text.replace('/**/', '').replace('_stockistAllStoresCallback(', '').replace(');', '')
        stores = json.loads(content)
        for store in stores:
            p_id = f'delta9 - {store["name"]}'
            store_url = ''
            for one in store['custom_fields']:
                if one['name'] == "Check In-Store Inventory":
                    store_url = one['value']
            if not store_url:
                store_url = store.get('website')

            producer = {"Producer ID": '',
                        "p_id": p_id,
                        "Producer": 'delta9',
                        "Description": "Delta 9 Cannabis Store is a chain of recreational Cannabis stores in Manitoba, Alberta, and Saskatchewan. Order Marijuana for same day delivery in Winnipeg or shop in our retail stores. Delta 9 Cannabis is also a large Licensed Producer of Marijuana. We are listed on the TSX under the stock ticker DN.",
                        "Link": store.get('website'),
                        "SKU": "",
                        "City": store.get("city"),
                        "Province": store.get("state"),
                        "Store Name": store.get("name"),
                        "Postal Code": store.get("postal_code"),
                        "long": store.get('longitude'),
                        "lat": store.get('latitude'),
                        "ccc": "",
                        "Page Url": store_url,
                        "Active": "",
                        "Main image": "hhttps://cdn.shopifycdn.net/s/files/1/0090/6438/2521/files/D9C_white-logo_transparent-bg_602x338.png",
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
                        "Email": store.get('email'),
                        "Social": "",
                        "FullAddress": f"{store.get('address_line_1')}, {store.get('city')}, "
                                       f"{store.get('state')} {store.get('postal_code')}",
                        "Address": store.get('address_line_1'),
                        "Additional Info": "",
                        "Created": "",
                        "Comment": "",
                        "Updated": ""}
            yield producer

            if store_url:
                yield scrapy.Request(store_url,
                                     callback=self.parse_store_inventory,
                                     meta={'p_id': p_id,
                                           'handle_httpstatus_list': [404]})

    def parse_store_inventory(self, response):
        if response.status == 404:
            if '/pages/' not in response.url:
                store_url = response.url.replace('delta9.ca/', 'delta9.ca/pages/')
                yield scrapy.Request(store_url,
                                     callback=self.parse_store_inventory,
                                     meta={'p_id': response.meta.get('p_id')})
            return

        data_json_url = response.xpath('//div[@class="productgrid--items-container"]'
                                       '/@data-json-url').extract_first()
        if not data_json_url:
            inventory_link = response.xpath('//li[@class="navmenu-item navmenu-id-check-inventory"]'
                                            '/a/@href').extract_first()
            if inventory_link:
                store_url = urljoin(response.url, inventory_link)
                yield scrapy.Request(store_url,
                                     callback=self.parse_store_inventory,
                                     meta={'p_id': response.meta.get('p_id')})
            return

        data_json_store = response.xpath('//div[@class="productgrid--items-container"]'
                                         '/@data-json-store').extract_first()
        url = f'{data_json_url}{data_json_store}.json'
        yield scrapy.Request(url,
                             callback=self.parse_list,
                             meta={'p_id': response.meta.get('p_id')})

    def parse_list(self, response):
        brands = self.settings.get('BRANDS', [])
        result = response.json()
        for category_id, products in result.items():
            for product_json in products:
                brand = product_json.get('vendor')
                if brand and brands and brand.strip() not in brands:
                    self.logger.debug(f'Ignore brand: {brand}')
                    continue

                html = HtmlResponse(url="", body=product_json["body_html"], encoding='utf-8')
                description = '\n'.join([x.strip() for x in html.xpath('//text()').extract() if x.strip()])

                featured_image = product_json.get('image')
                if featured_image:
                    featured_image = featured_image.get('src')

                cbd = thc = genetics = ''
                meta_fields = product_json.get('meta_fields')
                if meta_fields:
                    cbd = meta_fields.get('cbd_amount')
                    thc = meta_fields.get('thc_amount')
                    genetics = meta_fields.get('genetics')

                for variant in product_json['variants']:
                    product = {"Page URL": f'https://www.delta9.ca/products/{product_json["shopify_handle"]}',
                               "Brand": product_json.get('vendor'),
                               "Name": f'{product_json["title"]} - {variant["title"]}',
                               "SKU": variant.get('title'),
                               "Out stock status": 'In stock' if variant['inventory_quantity'] > 0 else 'Sold out',
                               "Stock count": variant.get('inventory_quantity', 0),
                               "Currency": "CAD",
                               "ccc": "",
                               "Price": variant['price'],
                               "Manufacturer": product_json.get('vendor'),
                               "Main image": featured_image,
                               "Description": description,
                               "Product ID": '',
                               "Additional Information": variant,
                               "Meta description": "",
                               "Meta title": "",
                               "Old Price": variant.get('compare_at_price'),
                               "Equivalency Weights": '',
                               "Quantity": '',
                               "Weight": variant.get('cannabis_weight'),
                               "Option": '',
                               "Option type": 'Select',
                               "Option Value": variant.get('title'),
                               "Option image": "",
                               "Option price prefix": variant['price'],
                               "Cat tree 1 parent": product_json.get('product_type'),
                               "Cat tree 1 level 1": '',
                               "Cat tree 1 level 2": "",
                               "Cat tree 2 parent": genetics,
                               "Cat tree 2 level 1": "",
                               "Cat tree 2 level 2": "",
                               "Cat tree 2 level 3": "",
                               "Image 2": '',
                               "Image 3": '',
                               "Image 4": '',
                               "Image 5": '',
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
                               "p_id": response.meta.get('p_id')}
                    yield product


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('delta9')
    process.start()
