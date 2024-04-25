import json
from typing import List

import scrapy
from websocket import create_connection
from Independent.spiders.base_spider import BaseSpider

PROXY_HOST = 'zproxy.lum-superproxy.io'
PROXY_PORT = '22225'
PROXY_USERNAME = 'lum-customer-c_731a4a5b-zone-static'
PROXY_PASSWORD = 'sjyy5ouxw8gr'


class GsyycSpider(BaseSpider):
    name = 'gsyyc'
    allowed_domains = ['gsyyc.ca']
    start_urls = ['https://www.gsyyc.ca/contact']

    def start_requests(self):
        products = self.query_products()

        # with open('products', 'r', encoding='utf-8') as f:
        #     products = json.load(f)

        yield scrapy.Request(self.start_urls[0],
                             meta={'products': products})

    def query_products(self) -> List[dict]:
        ws = create_connection(
            "wss://api2-clickspace-tv.firebaseio.com/.ws?v=5",
            http_proxy_host=PROXY_HOST,
            http_proxy_port=PROXY_PORT,
            http_proxy_auth=(PROXY_USERNAME, PROXY_PASSWORD)
        )
        result = ws.recv()
        self.logger.debug(result)

        ws.send('{"t":"d","d":{"r":1,"a":"s","b":{"c":{"sdk.js.8-2-6":1}}}}')
        result = ws.recv()
        self.logger.debug(result)

        ws.send('{"t":"d","d":{"r":2,"a":"q","b":{"p":"/iqmetrix/mergedList/ids'
                '/GreenspotShops-dot-Budvue/176375/2f1c2c895984b9650218bba0b1333072","h":""}}}')
        result1 = ws.recv()
        self.logger.debug(result1)
        result2 = ws.recv()
        self.logger.debug(result2)
        if 'mergedList/ids/GreenspotShops-dot-Budvue' in result1:
            result = json.loads(result1)
        elif 'mergedList/ids/GreenspotShops-dot-Budvue' in result2:
            result = json.loads(result2)
        else:
            result = None
            self.logger.error('No result returned')

        products = []
        if result:
            ids = result['d']['b']['d']
            base_p = result['d']['b']['p'].replace('/ids/', '/products/')
            for index, product_id in ids.items():
                msg = f'{{"t":"d","d":{{"r":{int(index) + 3},"a":"q","b":{{"p":"/{base_p}/{product_id}","h":""}}}}}}'
                ws.send(msg)
                response1 = ws.recv()
                self.logger.debug(response1)
                response2 = ws.recv()
                self.logger.debug(response2)

                if product_id in response1:
                    product = json.loads(response1)
                elif product_id in response2:
                    product = json.loads(response2)
                else:
                    self.logger.error(f'No product data: {product_id}')
                    break
                products.append(product['d']['b']['d'])
        ws.close()
        return products

    def parse(self, response, **kwargs):
        # Parse store data
        item = {"Producer ID": '',
                "p_id": 'gsyyc.ca',
                "Producer": f'Greenspot',
                "Description": response.xpath('//meta[@name="description"]/@content').extract_first(),
                "Link": 'https://www.gsyyc.ca/',
                "SKU": "",
                "City": 'Calgary',
                "Province": 'AB',
                "Store Name": 'Greenspot',
                "Postal Code": 'T2H 0L8',
                "long": '-114.074636',
                "lat": '50.9864052',
                "ccc": "",
                "Page Url": "https://www.gsyyc.ca/",
                "Active": "",
                "Main image": 'https://static.wixstatic.com/media/3f190e_2c4b627d12af42258dc5af62303d1973~mv2.png'
                              '/v1/fill/w_462,h_403,al_c,lg_1,q_85/greenspot.webp',
                "Image 2": '',
                "Image 3": '',
                "Image 4": '',
                "Image 5": '',
                "Type": "",
                "License Type": "",
                "Date Licensed": "",
                "Phone": '587 - 890 - 7768 ',
                "Phone 2": "",
                "Contact Name": "",
                "EmailPrivate": "",
                "Email": 'info@greenspotcanada.com',
                "Social": {'Facebook': 'https://www.facebook.com/GreenSpot-YYC-2459232941030169',
                           'Instagram': 'https://www.instagram.com/greenspotyyc/'},
                "FullAddress": '7523 Macleod Trail SW Calgary, AB Canada T2H 0L8',
                "Address": '7523 Macleod Trail SW',
                "Additional Info": '',
                "Created": "",
                "Comment": "",
                "Updated": ""}
        yield item

        # Parse products
        products = response.meta.get('products', [])
        for product in products:
            if "partDb" not in product:
                continue
            if 'variants' in product:
                for _, variant in product['variants'].items():
                    yield from self.parse_one(variant)
            else:
                yield from self.parse_one(product)

    def parse_one(self, product: dict):
        brand = product["partDb"]["brandName"]
        if product["partDb"]["brandName"].startswith('-'):
            brand = brand[1:]
        option = ''
        weight = ''
        if 'g' in product["partDb"]["netSizeUom"].lower():
            option = 'Weight'
            weight = f'{product["partDb"]["netSize"]}{product["partDb"]["netSizeUom"]}'
        elif product["partDb"]["netSizeUom"].lower() == 'ml':
            option = 'Volume'
        elif product["partDb"]["netSizeUom"]:
            self.logger.debug(product["partDb"]["netSizeUom"])

        if 'imageUrls' in product["partDb"]:
            images = list(product["partDb"]["imageUrls"].values())
            image_count = len(images)
        else:
            images = []
            image_count = 0

        if product["partDb"]["cbdMin"] == product["partDb"]["cbdMax"]:
            cbd = f'{product["partDb"]["cbdMin"]}{product["partDb"]["cbdUom"]}'
        else:
            cbd = f'{product["partDb"]["cbdMin"]}-{product["partDb"]["cbdMax"]}{product["partDb"]["cbdUom"]}'
        if product["partDb"]["thcMin"] == product["partDb"]["thcMax"]:
            thc = f'{product["partDb"]["thcMin"]}{product["partDb"]["thcUom"]}'
        else:
            thc = f'{product["partDb"]["thcMin"]}-{product["partDb"]["thcMax"]}{product["partDb"]["thcUom"]}'

        item = {
            "Page URL": f'https://www.gsyyc.ca/menu?product={product["partPos"]["id"]}',
            "Brand": brand,
            "Name": product["partDb"]["productName"],
            "SKU": product["partDb"]["sku"],
            "Out stock status": 'In stock' if product["partPos"]["inStock"] else 'Out of stock',
            "Stock count": product["partPos"]["stock"],
            "Currency": "CAD",
            "ccc": "",
            "Price": product["partPos"]["currentPriceNum"],
            "Manufacturer": product["partDb"]["supplier"],
            "Main image": product["partDb"].get('packageImageUrl'),
            "Description": product["partDb"]["longDescription"],
            "Product ID": product["partPos"]["id"],
            "Additional Information": product["partPos"]["specs"],
            "Meta description": '',
            "Meta title": '',
            "Old Price": product["partPos"]["regularPriceNum"],
            "Equivalency Weights": product["partPos"]["specs"]['Equivalent To'],
            "Quantity": product["partDb"]["piecesInPack"],
            "Weight": weight,
            "Option": option,
            "Option type": 'Select',
            "Option Value": product["partDb"]["netSizeSummary"],
            "Option image": "",
            "Option price prefix": product["partPos"]["currentPriceNum"],
            "Cat tree 1 parent": product["partDb"]["categories"].get('0'),
            "Cat tree 1 level 1": '',
            "Cat tree 1 level 2": "",
            "Cat tree 2 parent": product["partPos"]["categories"].get('0'),
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
            "Attribute 3": "strainType",
            "Attribute value 3": product["partDb"]["strainType"],
            "Attribute 4": "gramsCannabis",
            "Attribute value 4": product["partPos"]["gramsCannabis"],
            "Reviews": '',
            "Review link": '',
            "Rating": '',
            "Address": '',
            "p_id": 'gsyyc.ca'
        }
        yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('gsyyc')
    process.start()
