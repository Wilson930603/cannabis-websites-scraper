import demjson
import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class OcsSpider(BaseSpider):
    name = 'ocs'
    allowed_domains = ['ocs.ca', 'algolia.net']
    start_urls = ['https://ocs.ca/pages/store-locator']

    headers = {'accept': 'application/json',
               'content-type': 'application/x-www-form-urlencoded'}
    url_category = 'https://u2ghas8n0v-dsn.algolia.net/1/indexes/ocs_products_price_per_uom_asc/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.32.0&x-algolia-application-id=U2GHAS8N0V&x-algolia-api-key=0fce38bd280fd213b8a14f7a59602b7d'
    form_category = '{{"params":"distinct=true&hitsPerPage=12&page={}&analytics=false&filters=collections%3A{}%20AND%20variants_inventory_count%20%3E%200%20AND%20inventory_quantity%20%3E%200"}}'

    def parse(self, response, **kwargs):
        # Parse stores
        # indicator1 = '  storeToAdd = {'
        # indicator2 = '};'
        #
        # index2 = 0
        # while True:
        #     index1 = response.text.find(indicator1, index2)
        #     if index1 < 0:
        #         break
        #     index1 += len(indicator1)
        #     index2 = response.text.find(indicator2, index1)
        #     content = response.text[index1 - 1: index2 + 1]
        #     content = demjson.decode(content)
        #
        #     producer = {"Producer ID": '',
        #                 "p_id": f"ocs.ca - {content.get('id')}",
        #                 "Producer": 'ocs.ca',
        #                 "Description": content.get('en_content'),
        #                 "Link": content.get('website'),
        #                 "SKU": "",
        #                 "City": content.get('city'),
        #                 "Province": content.get('province'),
        #                 "Store Name": content.get('title'),
        #                 "Postal Code": content.get('zip'),
        #                 "long": content.get('longitude'),
        #                 "lat": content.get('latitude'),
        #                 "ccc": "",
        #                 "Page Url": 'https://ocs.ca/',
        #                 "Active": "",
        #                 "Main image": "https://cdn.shopifycdn.net/s/files/1/2636/1928/files/OCS_EN_LOGO_BLK_SM_nav_600x.png?v=1560138074",
        #                 "Image 2": '',
        #                 "Image 3": '',
        #                 "Image 4": '',
        #                 "Image 5": '',
        #                 "Type": "",
        #                 "License Type": "",
        #                 "Date Licensed": "",
        #                 "Phone": content.get('formatted_phone'),
        #                 "Phone 2": "",
        #                 "Contact Name": "",
        #                 "EmailPrivate": "",
        #                 "Email": content.get('email'),
        #                 "Social": "{Twitter: https://twitter.com/ONCannabisStore}",
        #                 "FullAddress": f"{content.get('address1')}, {content.get('city')}, {content.get('province')}",
        #                 "Address": content.get('address1'),
        #                 "Additional Info": "",
        #                 "Created": "",
        #                 "Comment": "",
        #                 "Updated": ""}
        #     yield producer

        # Parse product menu
        links = response.xpath('//ul/li/a[@class="menu__tier-three__link js-menu__tier-three__link"]/@href').extract()
        for link in links:
            if '/collections/' not in link:
                continue
            category = link.replace('/collections/', '')
            url = self.url_category.format(category)
            yield scrapy.Request(url,
                                 method='POST',
                                 headers=self.headers,
                                 body=self.form_category.format(0, category),
                                 callback=self.parse_list,
                                 meta={'category': category})

    def parse_list(self, response):
        result = response.json()
        if 'hits' not in result or not result['hits']:
            return

        brands = self.settings.get('BRANDS', [])
        for one in result['hits']:
            brand = one.get('vendor')
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            url = f'https://ocs.ca/products/{one["handle"]}'
            yield scrapy.Request(url,
                                 callback=self.parse_page,
                                 meta={'product_inventory': one})

        if result['page'] == 0:
            category = response.meta['category']
            for page in range(1, result['nbPages'] + 1):
                url = self.url_category.format(category)
                yield scrapy.Request(url,
                                     method='POST',
                                     headers=self.headers,
                                     body=self.form_category.format(page, category),
                                     callback=self.parse_list)

    def parse_page(self, response):
        product_inventory = response.meta['product_inventory']

        indicator = 'window.BOOMR.shopId = '
        index1 = response.text.find(indicator)
        index1 += len(indicator)
        index2 = response.text.find(';', index1)
        shop_id = f'ocs.ca - {response.text[index1: index2]}'

        indicator = 'window.theme.product_json = '
        index1 = response.text.find(indicator)
        index1 += len(indicator)
        index2 = response.text.find('};', index1)
        content = response.text[index1: index2 + 1]
        product_json = demjson.decode(content)

        featured_image = product_json.get('featured_image')
        if featured_image and not featured_image.startswith('https'):
            featured_image = f'https:{featured_image}'
        images = product_json.get('images', [])
        images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        image_count = len(images)

        category = None
        sub_category = None
        plant_type = None
        cbd_content_min = None
        cbd_content_max = None
        thc_content_min = None
        thc_content_max = None
        licensed_producer = None
        for tag in product_json.get('tags'):
            if tag.startswith('category--'):
                category = tag.replace('category--', '')
            elif tag.startswith('subcategory--'):
                sub_category = tag.replace('subcategory--', '')
            elif tag.startswith('plant_type--'):
                plant_type = tag.replace('plant_type--', '')
            elif tag.startswith('cbd_content_min--'):
                cbd_content_min = tag.replace('cbd_content_min--', '').replace('0000', '')
            elif tag.startswith('cbd_content_max--'):
                cbd_content_max = tag.replace('cbd_content_max--', '').replace('0000', '')
            elif tag.startswith('thc_content_min--'):
                thc_content_min = tag.replace('thc_content_min--', '').replace('0000', '')
            elif tag.startswith('thc_content_max--'):
                thc_content_max = tag.replace('thc_content_max--', '').replace('0000', '')
            elif tag.startswith('licensed_producer--'):
                licensed_producer = tag.replace('licensed_producer--', '')
        cbd = thc = None
        if cbd_content_min and cbd_content_max:
            cbd = f'{cbd_content_min} - {cbd_content_max} mg'
        elif cbd_content_min:
            cbd = f'{cbd_content_min} mg'
        elif cbd_content_max:
            cbd = f'{cbd_content_max} mg'
        if thc_content_min and thc_content_max:
            thc = f'{thc_content_min} - {thc_content_max} mg'
        elif thc_content_min:
            thc = f'{thc_content_min} mg'
        elif thc_content_max:
            thc = f'{thc_content_max} mg'

        variant_count = len(product_json['variants'])
        variants_inventory_count = product_inventory['variants_inventory_count']
        for variant in product_json['variants']:
            if product_inventory['sku'] == variant.get('sku'):
                variant['inventory'] = product_inventory['inventory_quantity']
                variants_inventory_count -= product_inventory['inventory_quantity']
            else:
                variant['inventory'] = None
        for variant in product_json['variants']:
            if not variant['inventory']:
                if variant_count == 2:
                    variant['inventory'] = variants_inventory_count
                else:
                    variant['inventory'] = f'?{variants_inventory_count}?'

        for variant in product_json['variants']:
            item = {"Page URL": f'https://ocs.ca/products/{product_json["handle"]}?variant={variant["id"]}',
                    "Brand": product_json.get('vendor'),
                    "Name": variant.get('name'),
                    "SKU": variant.get('sku'),
                    "Out stock status": 'In stock' if variant['available'] else 'Out of stock',
                    "Stock count": variant['inventory'],
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": variant.get('price') / 100,
                    "Manufacturer": licensed_producer,
                    "Main image": featured_image,
                    "Description": product_json.get('description'),
                    "Product ID": product_json.get('id'),
                    "Additional Information": '',
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant['option1'] if 'g' in variant['option1'] else '',
                    "Option": product_inventory['option_names'][0] if product_inventory['option_names'] else '',
                    "Option type": 'Select',
                    "Option Value": variant.get('option1'),
                    "Option image": "",
                    "Option price prefix": variant.get('price') / 100,
                    "Cat tree 1 parent": category,
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": sub_category,
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
                    "Attribute 3": "Plant Type",
                    "Attribute value 3": plant_type,
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant.get('id'),
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": shop_id}
            yield item

        indicator = 'window.theme.shop = '
        index1 = response.text.find(indicator)
        index1 += len(indicator)
        index2 = response.text.find('};', index1)
        content = response.text[index1: index2 + 1]
        store_json = demjson.decode(content)
        address = store_json['address']
        producer = {"Producer ID": '',
                    "p_id": shop_id,
                    "Producer": 'ocs.ca',
                    "Description": address.get('company'),
                    "Link": '',
                    "SKU": "",
                    "City": address.get('city'),
                    "Province": address.get('province'),
                    "Store Name": store_json.get('name'),
                    "Postal Code": address.get('zip'),
                    "long": address.get('longitude'),
                    "lat": address.get('latitude'),
                    "ccc": "",
                    "Page Url": store_json.get('url'),
                    "Active": "",
                    "Main image": "https://cdn.shopifycdn.net/s/files/1/2636/1928/files/OCS_EN_LOGO_BLK_SM_nav_600x.png?v=1560138074",
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
                    "Email": 'omeed.asadi@ocs.ca',
                    "Social": "{Twitter: https://twitter.com/ONCannabisStore}",
                    "FullAddress": f"{address.get('address1')}, {address.get('address2')}, {address.get('city')}, "
                                   f"{address.get('province')} {address.get('zip')}",
                    "Address": address.get('address1'),
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
        yield producer


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('ocs')
    process.start()
