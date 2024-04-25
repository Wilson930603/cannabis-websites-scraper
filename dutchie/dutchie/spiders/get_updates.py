import copy
import datetime
import json
from distutils.util import strtobool
import requests
import scrapy
from scrapy.exceptions import DontCloseSpider

from dutchie.spiders import api_parameters


class GetUpdatesSpider(scrapy.Spider):
    name = 'get_updates'
    allowed_domains = []
    can_province_abbrev = {
        'Alberta': 'AB',
        'British Columbia': 'BC',
        'Manitoba': 'MB',
        'New Brunswick': 'NB',
        'Newfoundland and Labrador': 'NL',
        'Northwest Territories': 'NT',
        'Nova Scotia': 'NS',
        'Nunavut': 'NU',
        'Ontario': 'ON',
        'Prince Edward Island': 'PE',
        'Quebec': 'QC',
        'Saskatchewan': 'SK',
        'Yukon': 'YT'
    }
    search_store_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "apollographql-client-name": "Marketplace (production)",
        "url": "https://dutchie.com/dispensaries",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "te": "trailers"
    }
    search_products_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "apollographql-client-name": "Marketplace (production)",
        "url": "https://dutchie.com/dispensary/spiritleaf-centre-st",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "te": "trailers"
    }
    search_products_url = 'https://dutchie.com/graphql?operationName=FilteredProducts&variables={{"productsFilter":{{"dispensaryId":"{0}","bypassOnlineThresholds":false}},"page":0,"perPage":5000}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{1}"}}}}'

    search_store_url = 'https://dutchie.com/graphql?operationName=DispensarySearch&variables={{"dispensaryFilter":{{"medical":false,"recreational":false,"sortBy":"distance","noMinimum":false,"activeOnly":true,"city":"Calgary","country":"Canada","nearLat":{0},"nearLng":{1},"destinationTaxState":"{2}","distance":15,"openNowForPickup":false,"acceptsCreditCardsPickup":false,"offerCurbsidePickup":false,"offerPickup":true}}}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{3}"}}}}'

    def __init__(self, city='', update_params="True", **kwargs):
        super().__init__(**kwargs)
        self.city = city.lower().replace("_", " ")
        self.csv_file_uploaded = False
        self.update_params = bool(strtobool(update_params))

    def start_requests(self):
        if self.update_params:
            api_parameters.get_parameters(self.settings.get('PROXY_URL'))
        self.hashes = requests.get('http://3.144.196.137:1240/get').json()

        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{self.city}.json?country=US%2CPR%2CCA%2CJM%2CVC&types=address%2Ccountry%2Cdistrict%2Clocality%2Cneighborhood%2Cplace%2Cpostcode%2Cregion&access_token=pk.eyJ1IjoiZHV0Y2hpZS1lbmciLCJhIjoiY2tkNjlxaGNlMG51ajJ4bzhjbTk5cG5zNyJ9.FEj8yCJEq36aac-v-N227w"
        yield scrapy.Request(url)

    def parse(self, response):
        try:
            data = response.json()
            if data:
                lat = data['features'][0]['center'][1]
                lng = data['features'][0]['center'][0]
                display_name = data['features'][0]["place_name"].split(', ')
                for name in display_name[::-1]:
                    name = name.strip()
                    if name in self.can_province_abbrev.keys():
                        state = self.can_province_abbrev[name]
                        break
                search_url = self.search_store_url.format(lat, lng, state, self.hashes["DispensarySearchHash"])
                yield scrapy.Request(
                    url=search_url,
                    headers=self.search_store_headers,
                    callback=self.parse_producers
                )
            else:
                print('City Data Not found...')
        except Exception as e:
            self.logger.error(response.text)

    def parse_producers(self, response):
        try:
            producer_data = json.loads(response.body)
            for dispen in producer_data["data"]["filteredDispensaries"]:
                header = copy.copy(self.search_products_headers)
                dispensary_id = dispen["id"]
                c_name = dispen["cName"]
                header['url'] = f"https://dutchie.com/dispensary/{c_name}"
                url = self.search_products_url.format(dispensary_id, self.hashes['ProductHash'])
                yield scrapy.Request(url=url, headers=header, callback=self.parse_products, meta={'Producer_ID': dispensary_id})
        except Exception as e:
            self.logger.error(response.url)
            self.logger.error(response.text)

    def parse_products(self, response):
        try:
            Producer_ID = response.meta["Producer_ID"]
            product_data = response.json()
            brands = self.settings.get('BRANDS')
            if "data" in product_data:
                for product in product_data["data"]["filteredProducts"]["products"]:
                    if brands and product["brandName"] not in brands:
                        self.logger.info(f'Ignore brand: {product["brandName"]}')
                        continue
                    if product['recSpecialPrices']:
                        price = product['recSpecialPrices'][0]
                    else:
                        price = product["Prices"][0]
                    yield {
                        "Producer ID": Producer_ID,
                        "Product ID": product['id'],
                        "Product Name": product["Name"],
                        "Stock Count": product["POSMetaData"]["children"][0]["quantityAvailable"],
                        "Product Price": price
                    }
        except Exception as e:
            self.logger.error(response.text)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('get_updates', city='Lloydminster,Alberta', update_params="false")
    process.start()
