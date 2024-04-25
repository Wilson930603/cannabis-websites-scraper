import json
from datetime import datetime
from urllib.parse import urljoin

import scrapy
from scrapy.http import HtmlResponse

from ShopifyBased.spiders.base_spider import BaseSpider


class ThefrontdeskSpider(BaseSpider):
    name = 'thefrontdesk'
    allowed_domains = ['thefrontdesk.ca']
    start_urls = ['https://www.thefrontdesk.ca/']
    custom_settings = {'COOKIES_ENABLED': True}

    # def start_requests(self):
    #     yield scrapy.Request('https://www.thefrontdesk.ca/products/delta-9-stargazer',
    #                          callback=self.parse_details,
    #                          meta={'dont_merge_cookies': True})

    def parse(self, response, **kwargs):
        links = response.xpath('//ul[@id="SiteNav"]/li/a/@href').extract()
        for link in links:
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_list,
                                 meta={'dont_merge_cookies': True})

    def parse_list(self, response):
        brands = self.settings.get('BRANDS', [])
        containers = response.xpath('//ul[@class="grid grid--uniform grid--view-items"]/li/div')
        for one in containers:
            name = one.xpath('a/span[@class="visually-hidden"]/text()').extract_first()
            if ' - ' in name:
                brand = name.split(' - ')[0]
            else:
                brand = ''
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                continue

            link = one.xpath('a/@href').extract_first()
            url = urljoin(self.start_urls[0], link)
            yield scrapy.Request(url,
                                 callback=self.parse_details,
                                 meta={'brand': brand,
                                       'dont_merge_cookies': True})

        next_page = response.xpath('//ul[@class="list--inline pagination"]/li'
                                   '/a[@class="btn btn--tertiary btn--narrow"]/@href').extract()
        if next_page:
            url = urljoin(self.start_urls[0], next_page[-1])
            yield scrapy.Request(url,
                                 callback=self.parse_list,
                                 meta={'dont_merge_cookies': True})

    def parse_details(self, response):
        product = response.xpath('//script[@id="ProductJson-product-template"]/text()').extract_first()
        if not product:
            return
        product = json.loads(product)

        if not response.meta.get('brand'):
            brands = self.settings.get('BRANDS', [])
            brand = product.get('vendor')
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                return

        html = HtmlResponse(url="", body=product["description"], encoding='utf-8')
        description = '\n'.join([x.strip() for x in html.xpath('//text()').extract() if x.strip()])

        thc = cbd = ''
        thc_cbd = html.xpath('//strong[contains(text(), "THC")]/text()').extract_first()
        if thc_cbd:
            parts = thc_cbd.split('CBD')
            if len(parts) == 2:
                thc = parts[0].replace('THC', '').strip()
                cbd = parts[-1].strip()
            else:
                if 'THC' in thc_cbd:
                    thc = thc_cbd.replace('THC', '').strip()
                elif 'CBD' in thc_cbd:
                    cbd = thc_cbd.replace('CBD', '').strip()
                else:
                    self.logger.error(thc_cbd)

        images = product.get('images')
        if images:
            image_count = len(images)
            images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        else:
            image_count = 0

        for variant in product['variants']:
            featured_image = variant.get('featured_image')
            if featured_image:
                featured_image = featured_image.get('src')

            item = {"Page URL": f"{response.url}?variant={variant['id']}",
                    "Brand": product.get('vendor'),
                    "Name": variant.get('name'),
                    "SKU": variant.get('sku'),
                    "Out stock status": 'In stock' if variant['available'] else 'Sold out',
                    "Stock count": 0,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": variant['price'] / 100,
                    "Manufacturer": product.get('vendor'),
                    "Main image": featured_image,
                    "Description": description,
                    "Product ID": product['id'],
                    "Additional Information": variant,
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": variant['compare_at_price'] / 100 if variant['compare_at_price'] else '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": variant.get('weight'),
                    "Option": product['options'][0] if 'options' in product and product['options'] else 'Variant',
                    "Option type": 'Select',
                    "Option Value": variant.get('option1'),
                    "Option image": "",
                    "Option price prefix": variant['price'] / 100,
                    "Cat tree 1 parent": product.get('type'),
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": '',
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
                    "Attribute 3": "barcode",
                    "Attribute value 3": variant.get('barcode'),
                    "Attribute 4": "SKU ID",
                    "Attribute value 4": variant['id'],
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": 'thefrontdesk.ca-Altona'}
            if not variant['available']:
                yield item
            else:
                url = f'https://www.thefrontdesk.ca//variants/{variant["id"]}/?section_id=store-availability'
                yield scrapy.Request(url,
                                     callback=self.pare_store,
                                     dont_filter=True,
                                     meta={'product': item,
                                           'dont_merge_cookies': True})

    def pare_store(self, response):
        address = response.xpath('//h3[@class="store-availability-list__location"]/text()').extract_first()
        full_address = response.xpath('//address[@class="store-availability-list__address"]/p/text()').extract()
        if len(full_address) > 1:
            parts = full_address[1].split(' ')
            city = parts[0]
            state = parts[1]
            zipcode = ' '.join(parts[2:])
            p_id = f'thefrontdesk.ca-{city}'
        else:
            city = state = zipcode = ''
            p_id = 'thefrontdesk.ca-Altona'
        phone = response.xpath('//p[contains(@class, "store-availability-list__phone")]/text()').extract_first()

        producer = {"Producer ID": '',
                    "p_id": p_id,
                    "Producer": 'thefrontdesk',
                    "Description": "We are located at the Front Desk of The Altona Hotel, Altona, MB. We sell a curated selection of popular cannabis products that can be purchase online, or through pick-up at the Front Desk. We are discreet and we are built on offering and exceptional and rebuttable safe experience in enjoying your favourite cannabis products where you know what you're getting. ",
                    "Link": 'https://www.thefrontdesk.ca/',
                    "SKU": "",
                    "City": city,
                    "Province": state,
                    "Store Name": p_id,
                    "Postal Code": zipcode,
                    "long": '',
                    "lat": '',
                    "ccc": "",
                    "Page Url": "https://www.thefrontdesk.ca/",
                    "Active": "",
                    "Main image": "https://cdn.shopifycdn.net/s/files/1/0559/2376/9516/files/Untitled_design_1_180x.jpg",
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Type": "",
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": phone.strip() if phone else '',
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": '',
                    "Social": "https://www.facebook.com/thefrontdeskaltona",
                    "FullAddress": ', '.join(full_address),
                    "Address": address.strip() if address else '',
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
        yield producer

        product = response.meta['product']
        product['p_id'] = p_id
        sku_id = product["Attribute value 4"]
        form_data = {"form_type": "product",
                     "utf8": "✓",
                     "id": str(sku_id)}
        yield scrapy.FormRequest('https://www.thefrontdesk.ca/cart/add.js',
                                 headers={'Accept': '*/*',
                                          'Alt-Used': 'www.thefrontdesk.ca',
                                          'Content-Type': 'application/x-www-form-urlencoded',
                                          'X-Requested-With': 'XMLHttpRequest'},
                                 dont_filter=True,
                                 formdata=form_data,
                                 callback=self.parse_add_cart,
                                 meta={'product': product,
                                       'dont_merge_cookies': False,
                                       'cookiejar': sku_id})

    def parse_add_cart(self, response):
        today = datetime.now().strftime('%a+%b+%d+%Y')
        form_data = {"updates[]": "100",
                     "note": f"\r\nDelivery+Details\r\n\r\nDate:+{today}\r\nTime:+11:30+-+11:45\r\nNote:+",
                     "checkout": "We're+Currently+Closed.+Pre-Order+for+Later"}
        yield scrapy.FormRequest('https://www.thefrontdesk.ca/cart',
                                 headers={'Alt-Used': 'www.thefrontdesk.ca',
                                          'Content-Type': 'application/x-www-form-urlencoded'},
                                 dont_filter=True,
                                 formdata=form_data,
                                 callback=self.parse_update_cart,
                                 meta={'product': response.meta['product'],
                                       'dont_merge_cookies': False,
                                       'cookiejar': response.meta['cookiejar']})

    def parse_update_cart(self, response):
        quantity = response.xpath('//div[@class="step__footer"]'
                                  '/input[@id="checkout_line_items_0_quantity"]/@value').extract_first()
        product = response.meta['product']
        if quantity:
            product['Stock count'] = int(quantity)
        yield product


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('thefrontdesk')
    process.start()
