import json
import unicodedata
from urllib.parse import urljoin

import scrapy
import usaddress
from lxml import html
from ShopifyBased.spiders.base_spider import BaseSpider


class BccannabisstoresSpider(BaseSpider):
    name = 'bccannabisstores'
    allowed_domains = ['bccannabisstores.com', 'goo.gl']
    start_urls = ['https://www.bccannabisstores.com/pages/store-locations']

    # def start_requests(self):
    #     yield scrapy.Request('https://www.bccannabisstores.com/collections/pre-rolls',
    #                          callback=self.parse_menu)

    def parse(self, response, **kwargs):
        # Parse menu
        links = response.xpath('//nav[@class="site-navigation"]/ul/li/ul/li'
                               '/a[contains(@class, "navmenu-link")]/@href').extract()
        for link in links:
            url = urljoin(self.start_urls[0], link)
            yield scrapy.Request(url,
                                 callback=self.parse_menu)

        # We'll need a pseudo location for all the products.
        yield from self._parse_store('bccannabisstores.com',
                                     'BC Cannabis Stores',
                                     '3383 Gilmore Way',
                                     'https://www.bccannabisstores.com/',
                                     '604-252-7400')

        # Parse store locations
        containers = response.xpath('//div[@class="page-content"]'
                                    '/div[@class="page--store-locations"]')
        for container in containers:
            store_id = container.xpath('div[@class="page--store-locations--store-hours-container"]'
                                       '/span[@data-store-locations-store-status-block-id]'
                                       '/@data-store-locations-store-status-block-id').extract_first()
            if store_id.isnumeric():
                store_id = f'bccannabisstores-{store_id}'
            location = container.xpath('div[@class="page--store-locations--store-info-container"]'
                                       '/div[@class="page--store-locations--store-info"]')
            store_name = location.xpath('h3[@class="store-name"]/text()').extract_first()
            full_address = []
            for p in location.xpath('p'):
                contents = p.xpath('.//text()').extract()
                full_address.append(' '.join([x.strip() for x in contents if x.strip()])
                                    .replace('Shop Now', '').replace('Coming Soon', ''))
            full_address = ' '.join(full_address)
            full_address = unicodedata.normalize("NFKD", full_address)
            if 'Shop' in full_address:
                full_address = full_address.split('Shop')[0].strip()
            elif 'Coming' in full_address:
                full_address = full_address.split('Coming')[0].strip()
            link = location.xpath('p/a/@href').extract_first()
            phone = location.xpath('a[@class="store-phone"]/text()').extract_first()
            if 'goo.gl' in link:
                yield scrapy.Request(link,
                                     callback=self.parse_google_link,
                                     meta={'store_id': store_id,
                                           'store_name': store_name,
                                           'full_address': full_address,
                                           'phone': phone})
            else:
                yield from self._parse_store(store_id, store_name, full_address, link, phone)

            # Shop button
            # shop_link = location.xpath('p/a[contains(@href, "bccannabisstores.com")]/@href').extract_first()
            # if shop_link:
            #     yield scrapy.Request(shop_link,
            #                          callback=self.parse_menu,
            #                          meta={'p_id': store_id})

    def parse_google_link(self, response):
        yield from self._parse_store(response.meta['store_id'],
                                     response.meta['store_name'],
                                     response.meta['full_address'],
                                     response.url,
                                     response.meta['phone'])

    def _parse_store(self,
                     store_id: str,
                     store_name: str,
                     full_address: str,
                     address_link: str,
                     phone: str):
        index1 = address_link.find('@')
        if index1 > 0:
            index2 = address_link.find('/', index1)
            coordinates = address_link[index1 + 1: index2]
            coordinates = coordinates.split(',')
            latitude = coordinates[0]
            longitude = coordinates[1]
        else:
            latitude = ''
            longitude = ''

        try:
            address = usaddress.tag(full_address)
            address = address[0]
            city = address.get("PlaceName")
        except:
            city = full_address.split(',')[-2].strip()

        if 'BC ' in full_address:
            state = 'BC'
            zipcode = full_address.split('BC ')[-1].strip()
        elif 'BC,' in full_address:
            state = 'BC'
            zipcode = full_address.split('BC,')[-1].strip()
        else:
            state_zip = full_address.split(',')[-1].strip()
            parts = state_zip.split(' ')
            state = parts[0]
            zipcode = ' '.join(parts[1:])

        if store_id == 'bccannabisstores.com':
            producer = 'BC Liquor Distribution Branch'
            city = 'Burnaby'
            state = 'BC'
            zipcode = 'V5G 4S1'
            page_url = 'https://www.bccannabisstores.com/'
        else:
            producer = f'BC Cannabis Stores - {store_name or city}'
            page_url = "https://www.bccannabisstores.com/pages/store-locations"

        producer = {"Producer ID": '',
                    "p_id": store_id,
                    "Producer": producer,
                    "Description": '',
                    "Link": '',
                    "SKU": "",
                    "City": city,
                    "Province": state,
                    "Store Name": 'BC Cannabis Stores',
                    "Postal Code": zipcode,
                    "long": longitude,
                    "lat": latitude,
                    "ccc": "",
                    "Page Url": page_url,
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
                    "Email": '',
                    "Social": "Facebook: https://www.facebook.com/bccstores, "
                              "Twitter: https://twitter.com/BCCannabisStore",
                    "FullAddress": full_address,
                    "Address": full_address.split(',')[0],
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
        yield producer

    def parse_menu(self, response):
        p_id = response.meta.get('p_id', 'bccannabisstores.com')
        brands = self.settings.get('BRANDS', [])

        containers = response.xpath('//div[@class="productgrid--items"]/article'
                                    '/div[@class="productitem"]')
        for container in containers:
            brand = container.xpath('div[@class="productitem--info"]'
                                    '/div[@class="productitem--info-upper"]'
                                    '/p[@class="productitem--brand"]/strong/text()').extract_first()
            brand = brand.replace('by ', '').strip() if brand else ''
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            link = container.xpath('a[@class="productitem--image-link"]/@href').extract_first()
            url = urljoin(self.start_urls[0], link)
            yield scrapy.Request(url,
                                 callback=self.parse_details,
                                 meta={'p_id': p_id,
                                       'brand': brand})

        next_page = response.xpath('//div[@class="pagination--container"]/ul[@class="pagination--inner"]'
                                   '/li[@class="pagination--next"]/a[@class="pagination--item"]/@href').extract_first()
        if next_page:
            url = urljoin(self.start_urls[0], next_page)
            yield scrapy.Request(url,
                                 callback=self.parse_menu,
                                 meta={'p_id': p_id})

    def parse_details(self, response):
        brand = response.meta.get('brand')

        json_data = response.xpath('//script[@data-section-id="static-product"]/text()').extract_first()
        if not json_data:
            return
        json_data = json.loads(json_data)
        product = json_data.get('product')
        availabilities = json_data.get('variantAvailabilities')

        images = product.get('images')
        if images:
            image_count = len(images)
            images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        else:
            image_count = 0

        category = ''
        for one in product['tags']:
            if 'subcategory' in one:
                category = one.replace('subcategory::', '')
            elif 'brand' in one:
                if not brand:
                    brand = one.replace('brand::', '')
        if not brand:
            brand = product.get('vendor', '')

        properties = {}
        lis = response.xpath('//ul[@class="product-characteristics"]'
                             '/li[@class="product-characteristic"]')
        for li in lis:
            key = li.xpath('span[@class="product-characteristic--key"]/text()').extract_first()
            value = li.xpath('span[@class="product-characteristic--value"]/text()').extract_first()
            properties[key] = value

        badge = response.xpath('//div[@class="product-pricing"]'
                               '/div[@data-product-badge]//text()').extract()
        badge = ' '.join([x.strip() for x in badge if x.strip()])
        description = html.fromstring(product.get('description')).text_content()

        for variant in product['variants']:
            if badge:
                out_of_stock_status = badge
            else:
                out_of_stock_status = 'In stock' if variant.get('available', False) else 'Out of Stock'
            # option_type = ''
            # if 'g' in variant.get('option1'):
            #     option_type = 'Weight'
            # elif 'ml' in variant.get('option1'):
            #     option_type = 'Volume'
            featured_image = variant.get('featured_image', '')
            if featured_image:
                featured_image = featured_image.get('src', '')

            item = {"Page URL": f"{response.url}?variant={variant['id']}",
                    "Brand":  brand or properties.get('Brand'),
                    "Name": variant.get('name'),
                    "SKU": variant.get('sku'),
                    "Out stock status": out_of_stock_status,
                    "Stock count": availabilities.get(str(variant['id'])).get('vq'),
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": variant['price'] / 100,
                    "Manufacturer": product.get('vendor'),
                    "Main image": featured_image,
                    "Description": description,
                    "Product ID": product['id'],
                    "Additional Information": properties,
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('weight'),
                    "Option": "Variant",
                    "Option type": 'Select',
                    "Option Value": variant.get('option1'),
                    "Option image": "",
                    "Option price prefix": variant['price'] / 100,
                    "Cat tree 1 parent": category,
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": product.get('type'),
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
                    "Attribute 3": "Product Type",
                    "Attribute value 3": properties.get('Type'),
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant['id'],
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": response.meta.get('p_id', 'bccannabisstores.com')}
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('bccannabisstores')
    process.start()
