import copy
import json
import re

import scrapy

from ShopifyBased.spiders.base_spider import LocationBaseSpider


class NovacannabisstoreSpiderLocation(LocationBaseSpider):
    name = 'novacannabisstore'
    allowed_domains = []
    start_urls = ['https://novacannabisstore.com/pages/store-locations']
    base_url = 'https://novacannabisstore.com'
    website_filter_id = '9900'

    # def start_requests(self):
    #     yield scrapy.Request('https://novacannabisstore.com/products/rgb-72-volt-s-dried-3-5g?variant=39252418756737',
    #                          callback=self.parse_details)

    def parse(self, response, **kwargs):
        storerocket_id = response.xpath('//div[@id="storerocket-widget"]/@data-storerocket-id').extract_first()
        # provinces = response.xpath('//div[@id="SiteNavLinklist-provinces"]/ul//li/a/text()').extract()
        for province, coord in self.locations.items():
            url = f'https://api.storerocket.io/api/user/{storerocket_id}/locations?' \
                  f'{coord}&radius=2500&filters=9900'
            yield scrapy.Request(url,
                                 headers={'Accept': 'application/json, text/javascript, */*; q=0.01'},
                                 callback=self.parse_location)

    def parse_details(self, response):
        json_product = response.xpath('//script[@id="ProductJson-product-template"]/text()').extract_first()
        json_product = json.loads(json_product)

        json_variant = response.xpath('//script[@id="VariantJson-product-template"]/text()').extract_first()
        json_variant = json.loads(json_variant)

        properties = {}
        for one in response.xpath('//div[@class="product_specs"]/div'):
            key = one.xpath('label/text()').extract_first()
            value = one.xpath('span/text()').extract_first()
            properties[key[:-1]] = value

        brands = self.settings.get('BRANDS', [])
        brand = properties.get('Brand Name')
        if brand and brands and brand not in brands:
            self.logger.debug(f'Ignore brand: {brand}')
            return

        thc = cbd = ''
        containers = response.xpath('//div[@class="product_specs thc_cbd"]/div')
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

        if json_variant:
            inventory_quantity = json_variant[0].get('inventory_quantity', '')
        else:
            inventory_quantity = ''

        images = [x['src'] for x in json_product['media']] if 'media' in json_product else []
        image_count = len(images)

        product_id = json_product['id']
        variants = json_product.get('variants')
        if not variants:
            self.logger.warning(response.url)
            return

        base_url = re.sub('collections/nova-cannabis-\w+/', '', response.url)
        for variant in variants:
            variant_id = variant['id']
            price = variant.get('price')
            if price is not None:
                try:
                    price = price / 100
                except:
                    self.logger.warning(price)

            item = {"Page URL": f"{base_url}?variant={variant_id}",
                    "Brand": properties.get('Brand Name'),
                    "Name": json_product.get('title'),
                    "SKU": variant.get('sku', ''),
                    "Out stock status": '',
                    "Stock count": inventory_quantity,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": price,
                    "Manufacturer": json_product.get('vendor'),
                    "Main image": variant.get('featured_image', ''),
                    "Description": json_product.get('description'),
                    "Product ID": product_id,
                    "Additional Information": properties,
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('weight', ''),
                    "Option": "",
                    "Option type": "",
                    "Option Value": "",
                    "Option image": "",
                    "Option price prefix": "",
                    "Cat tree 1 parent": json_product.get('type'),
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
                    "Attribute value 3": json_product.get('type'),
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant_id,
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": response.meta.get('store_id', '')}

            indicator = 'Shopify.shop = "'
            index1 = response.text.find(indicator)
            if index1 < 0:
                yield item
            else:
                index1 += len(indicator)
                index2 = response.text.find('";', index1)
                shop = response.text[index1: index2]
                url = f'https://inventorylocations.checkmyapp.net/product/' \
                      f'{shop}/{product_id}/{self.settings.get("LOCATION_COORDINATE", "0,0")}'
                yield scrapy.Request(url,
                                     callback=self.parse_stock_status,
                                     meta={'item': item,
                                           'variant_id': str(variant_id)})

    def parse_stock_status(self, response):
        variant_id = response.meta['variant_id']
        item = response.meta['item']

        location_status = {}
        result = json.loads(response.text)
        for v_id, variant in result['product']['variants'].items():
            if v_id != variant_id:
                continue

            locations = variant['inventoryItem']['locations']
            for one in locations:
                html = scrapy.http.HtmlResponse(url='null',
                                                body=one["available"],
                                                encoding='utf-8')
                available = html.xpath('//text()').extract_first()
                status = f'{one["name"]}: {available}'

                found = False
                p_id = None
                for _, store in self.stores.items():
                    if store['Postal Code'] == one['zip'] \
                            or store['Store Name'] in one['name'] \
                            or one['address'] in store['Address']:
                        found = True
                        p_id = store['p_id']
                        break
                if found:
                    location_status[p_id] = status
                else:
                    location_status[item['p_id']] = status

        if location_status:
            for p_id, status in location_status.items():
                item['p_id'] = p_id
                item["Out stock status"] = status
                yield item
        else:
            item["Out stock status"] = 'Currently not available at any nearby locations.'
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('novacannabisstore')
    process.start()
