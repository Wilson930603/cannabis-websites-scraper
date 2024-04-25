from urllib.parse import urljoin

import demjson
import scrapy

from ShopifyBased.spiders.base_spider import BaseSpider


class JupiterwinnipegSpider(BaseSpider):
    name = 'jupiterwinnipeg'
    allowed_domains = ['jupiterwinnipeg.ca']
    start_urls = ['https://jupiterwinnipeg.ca/']

    def parse(self, response, **kwargs):
        links = response.xpath('//nav[@id="AccessibleNav"]/ul/li//a/@href').extract()
        for link in links:
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_list)

    def parse_list(self, response):
        brands = self.settings.get('BRANDS', [])
        containers = response.xpath('//ul[@class="grid grid--uniform grid--view-items"]/li/div')
        for container in containers:
            brand = container.xpath('.//div[@class="price__vendor"]/dd/text()').extract_first()
            brand = brand.strip() if brand else ''
            if brand and brands and brand.strip() not in brands:
                self.logger.debug(f'Ignore brand: {brand}')
                return

            link = container.xpath('.//div[@class="submit-button-wrapper"]/a/@href').extract_first()
            url = urljoin(response.url, link)
            yield scrapy.Request(url,
                                 callback=self.parse_details)

        next_page = response.xpath('//ul[@class="list--inline pagination"]/li'
                                   '/a[@class="btn btn--tertiary btn--narrow"]/@href').extract()
        if next_page:
            url = urljoin(self.start_urls[0], next_page[-1])
            yield scrapy.Request(url,
                                 callback=self.parse_list)

    def parse_details(self, response):
        indicator = 'SECOMAPP.pl.product = '
        index1 = response.text.find(indicator)
        if index1 < 0:
            return
        index1 += len(indicator)
        index2 = response.text.find('};', index1)
        inventory = demjson.decode(response.text[index1: index2 + 1])

        option_type = response.xpath('//label[@for="SingleOptionSelector-0"]/text()').extract_first()
        option_type = option_type.strip() if option_type else ''

        for variant in inventory['variants']:
            url = f'{response.url}?variant={variant["id"]}&view=json'
            yield scrapy.Request(url,
                                 headers={'Accept': '*/*'},
                                 callback=self.parse_variant,
                                 meta={'inventory_quantity': variant['inventory_quantity'],
                                       'option_type': option_type})

    def parse_variant(self, response):
        product_json = response.json()

        cbd_min = cbd_max = thc_min = thc_max = 0
        category = equivalent_to = net_weight = ''
        for tag in product_json['tags']:
            if 'CBD Min' in tag:
                cbd_min = float(tag.replace('CBD Min:', '')) / 10
                cbd_min = cbd_min if cbd_min > int(cbd_min) else int(cbd_min)
            elif 'CBD Max' in tag:
                cbd_max = float(tag.replace('CBD Max:', '')) / 10
                cbd_max = cbd_max if cbd_max > int(cbd_max) else int(cbd_max)
            elif 'THC Min' in tag:
                thc_min = float(tag.replace('THC Min:', '')) / 10
                thc_min = thc_min if thc_min > int(thc_min) else int(thc_min)
            elif 'THC Max' in tag:
                thc_max = float(tag.replace('THC Max:', '')) / 10
                thc_max = thc_max if thc_max > int(thc_max) else int(thc_max)
            elif 'Equivalent To' in tag:
                equivalent_to = tag.replace('Equivalent To:', '')
            elif 'Net Weight' in tag:
                net_weight = tag.replace('Net Weight:', '')
            elif 'Health Canada Reporting Catego' in tag:
                category = tag.replace('Health Canada Reporting Catego:', '')

        if cbd_min < 1 and cbd_max < 1:
            cbd = '<1%'
        else:
            cbd = f'{cbd_min:.0f}% - {cbd_max:.0f}%'
        if thc_min < 1 and thc_max < 1:
            thc = '<1%'
        else:
            thc = f'{thc_min}% - {thc_max:.0f}%'

        images = product_json.get('images')
        if images:
            image_count = len(images)
            images = [f'https:{x}' if not x.startswith('https') else x for x in images]
        else:
            image_count = 0

        for variant in product_json['variants']:
            featured_image = variant.get('featured_image')
            if featured_image:
                featured_image = featured_image.get('src')

            product = {"Page URL": response.url.replace('&view=json', ''),
                       "Brand": product_json.get('vendor'),
                       "Name": variant.get('name'),
                       "SKU": variant.get('sku'),
                       "Out stock status": 'In stock' if variant['available'] else 'Sold out',
                       "Stock count": response.meta.get('inventory_quantity', 0),
                       "Currency": "CAD",
                       "ccc": "",
                       "Price": variant['price'] / 100,
                       "Manufacturer": product_json.get('vendor'),
                       "Main image": featured_image,
                       "Description": product_json.get('description'),
                       "Product ID": product_json['id'],
                       "Additional Information": variant,
                       "Meta description": "",
                       "Meta title": "",
                       "Old Price": variant['compare_at_price'] / 100 if variant['compare_at_price'] else '',
                       "Equivalency Weights": equivalent_to,
                       "Quantity": '',
                       "Weight": net_weight,
                       "Option": response.meta.get('option_type'),
                       "Option type": 'Select',
                       "Option Value": variant.get('option1'),
                       "Option image": "",
                       "Option price prefix": variant['price'] / 100,
                       "Cat tree 1 parent": category,
                       "Cat tree 1 level 1": '',
                       "Cat tree 1 level 2": "",
                       "Cat tree 2 parent": product_json.get('type'),
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
                       "p_id": 'jupiterwinnipeg.ca'}
            yield product

        store = product_json.get('store-availability')
        for name, location in store['locations'].items():
            address = location['address']
            producer = {"Producer ID": '',
                        "p_id": 'jupiterwinnipeg.ca',
                        "Producer": 'jupiterwinnipeg',
                        "Description": "Jupiter Cannabis - 580 Academy Road · Winnipeg’s newest weed and cannabis dispensary · Buy flower, pre-rolls, vapes, gummies, chocolate, drinks, cbd, and accessories.  Purchase online for same day delivery, click and collect, or have it shipped Canada Post in Manitoba. You Roll With Us Now.",
                        "Link": 'https://jupiterwinnipeg.ca/',
                        "SKU": "",
                        "City": address.get('city'),
                        "Province": address.get('province'),
                        "Store Name": name,
                        "Postal Code": address.get('zip'),
                        "long": address.get('longitude'),
                        "lat": address.get('latitude'),
                        "ccc": "",
                        "Page Url": "https://jupiterwinnipeg.ca/",
                        "Active": "",
                        "Main image": "https://cdn.shopifycdn.net/s/files/1/0508/5357/6885/files/JupiterCannabis_vert_colour_256x256_08bec844-55cd-457f-a09a-32a60a85ff09_360x.jpg",
                        "Image 2": '',
                        "Image 3": '',
                        "Image 4": '',
                        "Image 5": '',
                        "Type": "",
                        "License Type": "",
                        "Date Licensed": "",
                        "Phone": address.get('phone') or '(204) 306-4636',
                        "Phone 2": "",
                        "Contact Name": f"{address.get('first_name')} {address.get('last_name')}".strip(),
                        "EmailPrivate": "",
                        "Email": 'hey@jupiterwinnipeg.ca',
                        "Social": '{"Facebook": "https://www.facebook.com/jupiterwinnipeg",'
                                  '"Twitter": "https://twitter.com/jupitercannabis", '
                                  '"Pinterest": "https://pinterest.com/jupitercannabis", '
                                  '"Instagram": "https://www.instagram.com/jupitercannabis", '
                                  '"Snapchat": "https://www.snapchat.com/add/jupitercannabis"}',
                        "FullAddress": f"{address.get('address1')}, {address.get('city')}, "
                                       f"{address.get('province')} {address.get('zip')} {address.get('country')}",
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
    process.crawl('jupiterwinnipeg')
    process.start()
