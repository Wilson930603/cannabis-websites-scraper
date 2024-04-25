import json
import scrapy
from urllib.parse import urljoin

from Independent.spiders.base_spider import BaseSpider


class SqdcSpider(BaseSpider):
    name = 'sqdc'
    allowed_domains = ['sqdc.ca']
    start_urls = ['https://www.sqdc.ca/en-CA/Search?&fn1=InStock&fv1=in+store%7Conline']
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Content-Type': 'application/json',
               'WebsiteId': 'f3dbd28d-365f-4d3e-91c3-7b730b39b294',
               'X-Requested-With': 'XMLHttpRequest'}
    custom_settings = {'PROXY_URL': 'http://127.0.0.1:24001'}

    def parse(self, response, **kwargs):
        result = response.xpath('//div[@data-oc-controller="Product.SearchResults"]/@data-context').extract_first()
        if not result:
            return

        result = result.replace('&quot;', '"')
        result = json.loads(result)
        for product in result['SearchResults']:
            brand = product['Brand']
            url = urljoin(response.url, product['Url'])
            item = {"Page URL": url,
                    "Brand": brand,
                    "Name": product['DisplayName'],
                    "SKU": product['Sku'],
                    "Out stock status": 'InStock' if product['IsInStockInStores'] else 'OutOfStock',
                    "Stock count": 0,
                    "Currency": "CAD",
                    "ccc": "",
                    "Price": None,
                    "Manufacturer": '',
                    "Main image": product.get('ImageUrl'),
                    "Description": product.get('Description'),
                    "Product ID": product.get('ProductId'),
                    "Additional Information": '',
                    "Meta description": "",
                    "Meta title": "",
                    "Old Price": '',
                    "Equivalency Weights": "",
                    "Quantity": '',
                    "Weight": '',
                    "Option": "",
                    "Option type": '',
                    "Option Value": '',
                    "Option image": "",
                    "Option price prefix": '',
                    "Cat tree 1 parent": product.get('CategoryId'),
                    "Cat tree 1 level 1": '',
                    "Cat tree 1 level 2": "",
                    "Cat tree 2 parent": "",
                    "Cat tree 2 level 1": "",
                    "Cat tree 2 level 2": "",
                    "Cat tree 2 level 3": "",
                    "Image 2": '',
                    "Image 3": '',
                    "Image 4": '',
                    "Image 5": '',
                    "Sort order": "",
                    "Attribute 1": "SKU ID",
                    "Attribute Value 1": product.get('VariantId'),
                    "Attribute 2": "",
                    "Attribute value 2": '',
                    "Attribute 3": "",
                    "Attribute value 3": '',
                    "Attribute 4": "",
                    "Attribute value 4": '',
                    "Reviews": '',
                    "Review link": "",
                    "Rating": '',
                    "Address": '',
                    "p_id": None}
            yield scrapy.Request(url,
                                 callback=self.parse_details,
                                 meta={'product': item})

        next_page = response.xpath('//div[@class="pagination-dropdown "]/ul/li'
                                   '/a[@title="Next"]/@href').extract_first()
        if next_page:
            next_page = urljoin(response.url, next_page)
            yield scrapy.Request(next_page,
                                 callback=self.parse)

    def parse_details(self, response):
        product = response.meta['product']
        images = response.xpath('//div[@data-oc-click="selectImage"]/div/a/img/@data-zoom-src').extract()
        image_count = len(images)
        product["Image 2"] = images[0] if image_count > 0 else ''
        product["Image 3"] = images[1] if image_count > 1 else ''
        product["Image 4"] = images[2] if image_count > 2 else ''
        product["Image 5"] = images[3] if image_count > 3 else ''
        yield scrapy.Request('https://www.sqdc.ca/api/product/calculatePrices',
                             method='POST',
                             headers={'Accept': 'application/json, text/javascript, */*; q=0.01',
                                      'Content-Type': 'application/json',
                                      'WebsiteId': 'f3dbd28d-365f-4d3e-91c3-7b730b39b294',
                                      'X-Requested-With': 'XMLHttpRequest'},
                             body=f'{{"products":["{product["Product ID"]}"]}}',
                             callback=self.parse_price,
                             meta={'product': product})

    def parse_price(self, response):
        product = response.meta['product']
        data = response.json()
        variant_price = data['ProductPrices'][0]['VariantPrices'][0]
        product['Price'] = variant_price['DisplayPrice']
        # product['Old Price'] = variant_price['DisplayPrice']
        yield scrapy.Request('https://www.sqdc.ca/api/olivestoreinventory/getstoresinventory',
                             method='POST',
                             headers=self.headers,
                             body=f'{{"Sku":"{product["Attribute Value 1"]}","Page":1,"Pagesize":4}}',
                             callback=self.parse_inventory,
                             meta={'product': product})

    def parse_inventory(self, response):
        product = response.meta['product']
        data = response.json()
        for store in data['Stores']:
            product['p_id'] = store['Number']
            product["Out stock status"] = store['InventoryStatus']['DisplayName']
            product['Stock count'] = store['InventoryStatus']['Quantity']
            if product['Stock count'] < 1 and product["Out stock status"] == 'In Stock':
                product["Out stock status"] = 'Out Of Stock'
            yield product

            address = store['Address']
            producer = {"Producer ID": '',
                        "p_id": store['Number'],
                        "Producer": store['Name'],
                        "Description": '',
                        "Link": urljoin(response.url, store['Url']),
                        "SKU": "",
                        "City": address.get('City'),
                        "Province": address.get('RegionName'),
                        "Store Name": store['Name'],
                        "Postal Code": address.get('PostalCode'),
                        "long": address.get('Longitude'),
                        "lat": address.get('Latitude'),
                        "ccc": "",
                        "Page Url": "",
                        "Active": "",
                        "Main image": '',
                        "Image 2": '',
                        "Image 3": '',
                        "Image 4": '',
                        "Image 5": '',
                        "Type": "",
                        "License Type": "",
                        "Date Licensed": "",
                        "Phone": store.get('PhoneNumber'),
                        "Phone 2": "",
                        "Contact Name": "",
                        "EmailPrivate": "",
                        "Email": '',
                        "Social": {'Facebook': 'https://www.facebook.com/LaSQDC/',
                                   'Twitter': 'https://twitter.com/La_SQDC',
                                   'LinkedIn': 'https://www.linkedin.com/company/sqdc/'},
                        "FullAddress": f"{address.get('Line1')}, {address.get('City')}, {address.get('RegionName')} "
                                       f"{address.get('PostalCode')} {address.get('CountryName')}",
                        "Address": address.get('Line1'),
                        "Additional Info": "",
                        "Created": "",
                        "Comment": "",
                        "Updated": ""}
            yield producer

        if data['NextPage']:
            yield scrapy.Request('https://www.sqdc.ca/api/olivestoreinventory/getstoresinventory',
                                 method='POST',
                                 headers=self.headers,
                                 body=f'{{"Sku":"{product["Attribute Value 1"]}",'
                                      f'"Page":{data["NextPage"]["Page"]},"Pagesize":4}}',
                                 callback=self.parse_inventory,
                                 meta={'product': product})


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('sqdc')
    process.start()
