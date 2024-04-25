import json
from urllib.parse import urljoin

import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class PeicannabiscorpSpider(BaseSpider):
    name = 'peicannabiscorp'
    allowed_domains = ['peicannabiscorp.com']
    start_urls = ['https://peicannabiscorp.com/',
                  'https://peicannabiscorp.com/pages/contact']

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0],
                             callback=self.parse)
        yield scrapy.Request(self.start_urls[1],
                             callback=self.parse_contact)

    def parse(self, response, **kwargs):
        links = response.xpath('//ul[@class="site-nav__dropdown"]/div/li'
                               '/a[contains(@href, "/collections/")]/@href').extract()
        for link in links:
            yield scrapy.Request(urljoin(response.url, link),
                                 callback=self.parse_menu)

    def parse_contact(self, response):
        locations = response.xpath('//div[@class="locations"]/div[@class="location"]')
        for location in locations:
            name = location.xpath('h4/text()').extract_first()
            addresses = location.xpath('address/text()').extract()
            address = ' '.join(addresses)
            addresses = address.split(',')
            city = addresses[1].strip()
            state = addresses[-1].split(' ')[0]
            zipcode = addresses[-1].replace(state, '').strip()
            phone = location.xpath('a[contains(@href, "tel:")]/text()').extract_first()

            producer = {"Producer ID": '',
                        "p_id": f'peicannabiscorp.com - {name}',
                        "Producer": 'peicannabiscorp.com',
                        "Description": 'The Prince Edward Island Cannabis Management Corporation (PEICMC), under the branded name PEI Cannabis, is responsible for the distribution and sale of adult use cannabis in PEI, in partnership with the PEI Liquor Control Commission (PEILCC), and under the authority of the Cannabis Control Act. '
                                       '\nWe are committed to keeping cannabis out of the hands of people under the age of 19; educating Islanders on the health risks and regulations associated with cannabis use; and eliminating the illicit cannabis market. '
                                       '\nAs a retailer focused on upholding its regulatory obligations and encouraging responsible consumption, we are focused on investing in initiatives that promote responsible use and mitigating all consumption risks related to public health and safety. '
                                       '\nOur four retail locations on PEI are staffed with a highly trained and engaged team who provide the information our valued customers need to make the right choices.',
                        "Link": '',
                        "SKU": "",
                        "City": city,
                        "Province": state,
                        "Store Name": name,
                        "Postal Code": zipcode,
                        "long": '',
                        "lat": '',
                        "ccc": "",
                        "Page Url": 'https://peicannabiscorp.com/',
                        "Active": "",
                        "Main image": "https://cdn.shopify.com/s/files/1/0030/6639/6729/t/5/assets/logo-cannabis.svg",
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
                        "Email": 'infopeicmc@peicannabiscorp.com',
                        "Social": "Facebook: https://facebook.com/peicmc, "
                                  "Twitter: https://twitter.com/PEICannabis, "
                                  "Instagram: http://instagram.com/peicannabis",
                        "FullAddress": address,
                        "Address": addresses[0],
                        "Additional Info": "",
                        "Created": "",
                        "Comment": "",
                        "Updated": ""}
            yield producer

    def parse_menu(self, response):
        brands = self.settings.get('BRANDS', [])
        if brands:
            brands = [x.lower() for x in brands]
            links = response.xpath('//div[@class="product-filters__group brand_name"]/ul'
                                   '/li[@data-group="BRAND_NAME"]/a')
            for link in links:
                brand = link.xpath('text()').extract_first().strip()
                if brand.lower() in brands:
                    url = urljoin(response.url, link.xpath('@href').extract_first())
                    yield scrapy.Request(url,
                                         callback=self.parse_list,
                                         meta={'brand': brand})
        else:
            yield from self.parse_list(response)

    def parse_list(self, response):
        links = response.xpath('//div[@class="product_grid_item_wrapper"]/p[@class="h3"]/a/@href').extract()
        for link in links:
            yield scrapy.Request(urljoin(response.url, link),
                                 callback=self.parse_page,
                                 meta={'brand': response.meta.get('brand')})

        current_page = response.meta.get('page', 1)
        if current_page == 1:
            pages = response.xpath('//div[@class="pagination text-center"]/a/text()').extract()
            if pages:
                max_pages = int(pages[-1])
                for page in range(2, max_pages + 1):
                    if 'page=' in response.url:
                        url = response.url.replace('page=1', f'page={page}')
                    else:
                        url = f'{response.url}?page={page}'
                    yield scrapy.Request(url,
                                         callback=self.parse_list,
                                         meta={'brand': response.meta.get('brand'),
                                               'page': page})

    def parse_page(self, response):
        brand_meta = response.meta.get('brand')

        thc = response.xpath('//p[@class="product-meta"]/span[contains(text(), "THC:")]/text()').extract_first()
        thc = thc.replace('THC:', '').strip() if thc else ''
        cbd = response.xpath('//p[@class="product-meta"]/span[contains(text(), "CBD:")]/text()').extract_first()
        cbd = cbd.replace('CBD:', '').strip() if thc else ''

        option = response.xpath('//form[@id="AddToCartForm--product-template"]'
                                '/div[@class="form__row"]/div[@class="form__column"]/label/text()').extract_first()

        product_json = response.xpath('//script[@id="ProductJson-product-template"]/text()').extract_first()
        product_json = json.loads(product_json)

        featured_image = product_json.get('featured_image')
        if featured_image and not featured_image.startswith('https'):
            featured_image = f'https:{featured_image}'
        images = product_json.get('images', [])
        images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        image_count = len(images)

        brand_tag = None
        category = None
        item_type = None
        forms = None
        for tag in product_json.get('tags'):
            if tag.startswith('BRAND_NAME:'):
                brand_tag = tag.replace('BRAND_NAME:', '')
            elif tag.startswith('CATEGORY:'):
                category = tag.replace('CATEGORY:', '')
            elif tag.startswith('ITEM_TYPE:'):
                item_type = tag.replace('ITEM_TYPE:', '')
            elif tag.startswith('FORMS:'):
                forms = tag.replace('FORMS:', '')

        for variant in product_json['variants']:
            sku = variant.get('sku')
            if not sku:
                continue

            item = {"Page URL": f'{response.url}?variant={variant.get("id")}',
                    "Brand": brand_meta or brand_tag,
                    "Name": variant.get('title'),
                    "SKU": sku,
                    "Out stock status": 'In stock' if variant['available'] else 'Out of stock',
                    "Stock count": response.xpath(f'//option[@value="{variant["id"]}"]/@data-quantity').extract_first(),
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
                    "Weight": variant['option2'] if 'g' in variant['option2'] else '',
                    "Option": option,
                    "Option type": 'Select',
                    "Option Value": variant.get('option2'),
                    "Option image": "",
                    "Option price prefix": variant.get('price') / 100,
                    "Cat tree 1 parent": category,
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": item_type,
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
                    "Attribute 3": "Product Type",
                    "Attribute value 3": forms,
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant.get('id'),
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": 'peicannabiscorp.com'}
            yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('peicannabiscorp')
    process.start()
