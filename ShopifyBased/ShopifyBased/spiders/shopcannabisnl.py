import html
import json

import demjson
import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class ShopcannabisnlSpider(BaseSpider):
    name = 'shopcannabisnl'
    allowed_domains = ['shopcannabisnl.com', 'algolianet.com', 'algolia.net']
    start_urls = ['https://shopcannabisnl.com/',
                  'https://shopcannabisnl.com/apps/store-locator']

    headers = {'accept': 'application/json',
               'content-type': 'application/x-www-form-urlencoded'}
    url_brand = 'https://0zlhytomi0-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.27.0%3Binstantsearch.js%202.8.0%3BJS%20Helper%202.26.0&x-algolia-application-id=0ZLHYTOMI0&x-algolia-api-key=c1c78e92776e8528b0de22e818a47671'
    form_data_brand = '{{"requests":[{{"indexName":"shopify_products","params":"query=&hitsPerPage=10&page={0}&distinct=100&filters=tags%3Ab2c%20AND%20NOT%20meta.field.do_not_display%3Atrue%20AND%20collections%3A{1}&facets=%5B%22meta.field.brand%22%2C%22inventory_quantity%22%2C%22options.title%22%2C%22product_type%22%2C%22meta.field.class%22%2C%22meta.field.plant_type%22%2C%22meta.field.terpenes%22%2C%22options.flavour%22%2C%22meta.field.thc_range_min_mg%22%2C%22meta.field.thc_range_max_mg%22%2C%22meta.field.thc_range_min_unit%22%2C%22meta.field.thc_range_max_unit%22%2C%22meta.field.thc_range_min%22%2C%22meta.field.thc_range_max%22%2C%22meta.field.cbd_range_min_mg%22%2C%22meta.field.cbd_range_max_mg%22%2C%22meta.field.cbd_range_min_unit%22%2C%22meta.field.cbd_range_max_unit%22%2C%22meta.field.cbd_range_min%22%2C%22meta.field.cbd_range_max%22%2C%22meta.field.carrier_oil%22%2C%22meta.field.organic%22%5D&tagFilters="}}]}}'
    url_all = 'https://0zlhytomi0-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.27.0%3Binstantsearch.js%202.8.0%3BJS%20Helper%202.26.0&x-algolia-application-id=0ZLHYTOMI0&x-algolia-api-key=c1c78e92776e8528b0de22e818a47671'
    form_data_all = '{{"requests":[{{"indexName":"shopify_products","params":"query=&hitsPerPage=10&page={0}&distinct=100&filters=tags%3Ab2c%20AND%20NOT%20meta.field.do_not_display%3Atrue%20AND%20collections%3Aall&facets=%5B%22meta.field.brand%22%2C%22inventory_quantity%22%2C%22options.title%22%2C%22product_type%22%2C%22meta.field.class%22%2C%22meta.field.plant_type%22%2C%22meta.field.terpenes%22%2C%22options.flavour%22%2C%22meta.field.thc_range_min_mg%22%2C%22meta.field.thc_range_max_mg%22%2C%22meta.field.thc_range_min_unit%22%2C%22meta.field.thc_range_max_unit%22%2C%22meta.field.thc_range_min%22%2C%22meta.field.thc_range_max%22%2C%22meta.field.cbd_range_min_mg%22%2C%22meta.field.cbd_range_max_mg%22%2C%22meta.field.cbd_range_min_unit%22%2C%22meta.field.cbd_range_max_unit%22%2C%22meta.field.cbd_range_min%22%2C%22meta.field.cbd_range_max%22%2C%22meta.field.carrier_oil%22%2C%22meta.field.organic%22%5D&tagFilters="}}]}}'

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],
                             callback=self.parse)
        yield scrapy.Request(self.start_urls[1],
                             callback=self.parse_stores)

    def parse(self, response, **kwargs):
        brands = self.settings.get('BRANDS', [])
        if brands:
            brands = [x.lower() for x in brands]
            title = response.xpath('//div[contains(concat(" ", normalize-space(text()), " "), '
                                   '"Shop Brands by these suppliers")]')
            lis = title.xpath('following-sibling::ul[1]/li/div/ul[@class="sidebar-item__details-items"]/li')
            for li in lis:
                brand = li.xpath('a/text()').extract_first().strip()
                if brand.lower() in brands:
                    yield scrapy.Request(self.url_brand,
                                         method='POST',
                                         headers=self.headers,
                                         body=self.form_data_brand.format(0, brand),
                                         callback=self.parse_list,
                                         meta={'brand': brand})
        else:
            yield scrapy.Request(self.url_all,
                                 method='POST',
                                 headers=self.headers,
                                 body=self.form_data_all.format(0),
                                 callback=self.parse_list,
                                 meta={'brand': 'all'})

    def parse_stores(self, response):
        indicator1 = 'markersCoords.push('
        indicator2 = ');'

        index2 = 0
        while True:
            index1 = response.text.find(indicator1, index2)
            if index1 < 0:
                break
            index2 = response.text.find(indicator2, index1)
            content = html.unescape(response.text[index1 + len(indicator1): index2])
            content = content.replace('address:\'', 'address:"').replace('\'}', '"}')
            if 'data.you.lat' in content:
                break
            content = demjson.decode(content)

            addresses = scrapy.http.HtmlResponse(url="",
                                                 body=content['address'],
                                                 encoding='utf-8')
            name = addresses.xpath("//span[@class='name']/text()").extract_first().strip()
            address = addresses.xpath("//span[@class='address']/text()").extract_first().strip()
            phone = addresses.xpath("//span[@class='phone']/text()").extract_first()
            phone = phone.strip() if phone else None

            city_span = addresses.xpath("//span[@class='city']")
            city = city_span.xpath('text()').extract_first().strip()
            state = city_span.xpath('following-sibling::span[1]/text()').extract_first().strip()

            producer = {"Producer ID": '',
                        "p_id": content.get('id'),
                        "Producer": 'shopcannabisnl.com',
                        "Description": 'Welcome to Cannabis NL, a division of the Newfoundland Labrador Liquor Corporation (NLC).'
                                       '\nOn November 23, 2017, the Government of Newfoundland and Labrador authorized NLC to regulate the possession, sale and delivery of non-medical cannabis. Included in these new responsibilities was the authority to list products, set pricing and to be the exclusive online retailer of non-medical cannabis in the province.'
                                       '\nThis new mandate spawned the need to create a unique brand to differentiate the lines of business within the Corporation, which includes NLC Liquor Stores, Liquor Express, Rock Spirits, and now Cannabis NL.',
                        "Link": '',
                        "SKU": "",
                        "City": city,
                        "Province": state,
                        "Store Name": name,
                        "Postal Code": '',
                        "long": content.get('lng'),
                        "lat": content.get('lat'),
                        "ccc": "",
                        "Page Url": 'https://shopcannabisnl.com/',
                        "Active": "",
                        "Main image": "https://cdn.shopifycdn.net/s/files/1/0050/8916/5430/files/screen-shot-2018-05-29-at-12-29-43-pm-copy_600x.png",
                        "Image 2": '',
                        "Image 3": '',
                        "Image 4": '',
                        "Image 5": '',
                        "Type": "",
                        "License Type": "",
                        "Date Licensed": "",
                        "Phone": phone or '(709) 724-1200',
                        "Phone 2": "",
                        "Contact Name": "",
                        "EmailPrivate": "",
                        "Email": 'info@shopcannabisnl.com',
                        "Social": "Facebook: https://www.facebook.com/ShopCannNL, "
                                  "Twitter: https://twitter.com/ShopCannabisNl, "
                                  "Instagram: https://www.instagram.com/shopcannabisnl/",
                        "FullAddress": f"{address}, {city}, {state}",
                        "Address": address,
                        "Additional Info": "",
                        "Created": "",
                        "Comment": "",
                        "Updated": content.get('updated_at')}
            yield producer

    def parse_list(self, response):
        result = response.json()
        if 'results' not in result or not result['results']:
            return

        result = result['results'][0]
        for one in result['hits']:
            url = f'https://shopcannabisnl.com/products/{one["handle"]}'
            yield scrapy.Request(url,
                                 callback=self.parse_page)

        if result['page'] == 0:
            brand = response.meta['brand']
            for page in range(1, result['nbPages'] + 1):
                if brand == 'all':
                    yield scrapy.Request(self.url_all,
                                         method='POST',
                                         headers=self.headers,
                                         body=self.form_data_all.format(page),
                                         callback=self.parse_list)
                else:
                    yield scrapy.Request(self.url_brand,
                                         method='POST',
                                         headers=self.headers,
                                         body=self.form_data_brand.format(page, brand),
                                         callback=self.parse_list)

    def parse_page(self, response):
        properties = {}
        lis = response.xpath('//ul[@class="product-info__quick-stats"]/li[@class="product-info__quick-stat"]')
        for li in lis:
            title = li.xpath('h3/text()').extract_first().strip()
            value = li.xpath('span/text()').extract_first()
            properties[title] = value.strip() if value else ''

        indicator = 'window.theme.current_object ='
        index1 = response.text.find(indicator)
        if index1 < 0:
            return
        index1 += len(indicator)
        index2 = response.text.find('};', index1)
        content = response.text[index1: index2 + 1]
        product_json = json.loads(content, strict=False)

        featured_image = product_json.get('featured_image')
        if featured_image and not featured_image.startswith('https'):
            featured_image = f'https:{featured_image}'
        images = product_json.get('images', [])
        images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        image_count = len(images)

        brand_tag = None
        sub_department = None
        class_type = None
        # department = None
        for tag in product_json.get('tags'):
            if tag.startswith('brand::'):
                brand_tag = tag.replace('brand::', '')
            elif tag.startswith('SubDepartment::'):
                sub_department = tag.replace('SubDepartment::', '')
            elif tag.startswith('Class::'):
                class_type = tag.replace('Class::', '')
            # elif 'Department::' in tag:
            #     department = tag.replace('Department::', '')

        indicator = 'theme.products.update('
        index1 = response.text.find(indicator)
        index1 += len(indicator)
        index2 = response.text.find('});', index1)
        content = response.text[index1: index2 + 1]
        product_inventory = demjson.decode(content)

        for variant in product_json['variants']:
            inventory_quantity = None
            for one in product_inventory['variants']:
                if one['id'] == variant['id']:
                    inventory_quantity = one['inventory_quantity']
                    break

            item = {"Page URL": f'{response.url}?variant={variant.get("id")}',
                    "Brand": brand_tag,
                    "Name": variant.get('name'),
                    "SKU": variant.get('sku'),
                    "Out stock status": 'In stock' if variant['available'] else 'Out of stock',
                    "Stock count": inventory_quantity if inventory_quantity else '',
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": variant.get('price') / 100,
                    "Manufacturer": product_json.get('vendor'),
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
                    "Option": product_inventory['options_with_values'][0]['name'],
                    "Option type": 'Select',
                    "Option Value": variant.get('option1'),
                    "Option image": "",
                    "Option price prefix": variant.get('price') / 100,
                    "Cat tree 1 parent": sub_department,
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": class_type,
                    "Cat tree 2 level 1": "",
                    "Cat tree 2 level 2": "",
                    "Cat tree 2 level 3": "",
                    "Image 2": images[0] if image_count > 0 else '',
                    "Image 3": images[1] if image_count > 1 else '',
                    "Image 4": images[2] if image_count > 2 else '',
                    "Image 5": images[3] if image_count > 3 else '',
                    "Sort order": "",
                    "Attribute 1": "CBD",
                    "Attribute Value 1": properties.get('CBD'),
                    "Attribute 2": "THC",
                    "Attribute value 2": properties.get('THC'),
                    "Attribute 3": "Plant Type",
                    "Attribute value 3": properties.get('Plant Type'),
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant.get('id'),
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": 'shopcannabisnl.com'}
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('shopcannabisnl')
    process.start()
