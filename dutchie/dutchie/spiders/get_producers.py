import copy
import datetime
import json
from distutils.util import strtobool
import requests
import scrapy
from scrapy.exceptions import DontCloseSpider

from dutchie.spiders import api_parameters


class GetProducersSpider(scrapy.Spider):
    name = 'get_producers'
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
    search_address_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "apollographql-client-name": "Marketplace (production)",
        "url": "https://dutchie.com/dispensary/spiritleaf-centre-st/product/black-cherry-punch-1g",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "if-none-match": "W/\"6801-aLCLi46XpsLKEDyn6XNXxFmA1nM\"",
        "te": "trailers"
    }
    search_store_url = 'https://dutchie.com/graphql?operationName=DispensarySearch&variables={{"dispensaryFilter":{{"medical":false,"recreational":false,"sortBy":"distance","noMinimum":false,"activeOnly":true,"city":"Calgary","country":"Canada","nearLat":{0},"nearLng":{1},"destinationTaxState":"{2}","distance":15,"openNowForPickup":false,"acceptsCreditCardsPickup":false,"offerCurbsidePickup":false,"offerPickup":true}}}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{3}"}}}}'
    search_address_url = 'https://dutchie.com/graphql?operationName=ConsumerDispensaries&variables={{"dispensaryFilter": {{"cNameOrID": "{0}"}}}}&extensions={{"persistedQuery":{{"version":1,"sha256Hash":"{1}"}}}}'

    def __init__(self, city='', update_params="True", **kwargs):
        super().__init__(**kwargs)
        self.city = city.lower().replace("_", " ")

        # cwd = os.getcwd()
        # self.output_path = cwd + '\\output\\'
        # if not os.path.exists(self.output_path):
        #     os.makedirs(self.output_path)

        self.csv_file_uploaded = False
        self.update_params = bool(strtobool(update_params))

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(GetProducersSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     crawler.signals.connect(spider.spider_idle, signal=scrapy.signals.spider_idle)
    #     return spider
    #
    # def spider_idle(self):
    #     """ Waits for request to be scheduled.
    #     :return: None
    #     """
    #     if not self.csv_file_uploaded:
    #         start_time = self.crawler.stats.get_value('start_time')
    #         finish_time = self.crawler.stats.get_value('finish_time')
    #         if not finish_time:
    #             finish_time = datetime.datetime.now()
    #         total_run_time = (finish_time - start_time).seconds
    #         file_path = f'{self.settings.get("DATA_FILE_PATH")}/Producers_{self.city}.csv'
    #         url = f'https://{self.settings.get("WEBHOOK_KEY")}.azurewebsites.net/api/Function1?' \
    #               f'code=qrvGmnQhbRCi52jaZQ19fv98W0TySZXZOpjFTzO3W31UoeqJArZB7w==' \
    #               f'&name={file_path}&runtime={total_run_time}'
    #         request = scrapy.Request(url,
    #                                  # headers={},
    #                                  callback=self.parse_upload_result)
    #         self.crawler.engine.crawl(request, self)
    #         raise DontCloseSpider
    #
    # def parse_upload_result(self, response):
    #     self.logger.debug(response.text)
    #     self.csv_file_uploaded = True

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
        headers = copy.copy(self.search_address_headers)
        try:
            producer_data = json.loads(response.body)
            for dispen in producer_data["data"]["filteredDispensaries"]:
                item = {"Producer ID": "",
                        "p_id": dispen["id"],
                        "Producer": dispen["name"],
                        "Description": '',
                        "Link": f'https://dutchie.com/dispensaries/{dispen["cName"]}',
                        "SKU": "",
                        "City": "",
                        "Province": "",
                        "Store Name": dispen["name"],
                        "Postal Code": "",
                        "long": "",
                        "lat": "",
                        "ccc": "",
                        "Page Url": "",
                        "Active": "",
                        "Main image": dispen["listImage"] if dispen[
                            "listImage"] else 'https://neobi.io/images/coming-soon.jpg',
                        "Image 2": "",
                        "Image 3": "",
                        "Image 4": "",
                        "Image 5": "",
                        "Type": dispen["__typename"] if dispen["__typename"] else 'Unknown',
                        "License Type": "",
                        "Date Licensed": "",
                        "Phone": '',
                        "Phone 2": "",
                        "Contact Name": "",
                        "EmailPrivate": "",
                        "Email": '',
                        "Social": "",
                        "FullAddress": "",
                        "Address": "",
                        "Additional Info": "",
                        "Created": datetime.datetime.today(),
                        "Comment": "",
                        "Updated": None}

                url = self.search_address_url.format(dispen["cName"], self.hashes['DispensaryHash'])
                headers['url'] = f'https://dutchie.com/dispensaries/{dispen["cName"]}/menu'
                yield scrapy.Request(url,
                                     headers=headers,
                                     callback=self.parse_address,
                                     meta={'item': item})
                # yield item
        except Exception as e:
            self.logger.error(response.url)
            self.logger.error(response.text)

    def parse_address(self, response):
        item = response.meta['item']
        if response.status == 200:
            data = json.loads(response.text)
            if 'data' not in data:
                yield item
                self.logger.error(response.text)
                return

            data = data['data']['filteredDispensaries']
            if data:
                data = data[0]
                item["Phone"] = data.get('phone')
                item["Address"] = data.get('address')
                item['Producer'] = f"{item['Producer']} - {item['Address']}"
                item["Description"] = data.get('description')

                location = data.get('location')
                if location:
                    item['City'] = location.get('city')
                    item['Province'] = location.get('state')

                    if 'geometry' in location and location['geometry']:
                        if 'coordinates' in location['geometry'] and location['geometry']['coordinates']:
                            item['long'] = location['geometry']['coordinates'][0]
                            item['lat'] = location['geometry']['coordinates'][1]
        yield item


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    process = CrawlerProcess(get_project_settings())
    process.crawl('get_producers', city='Lloydminster,Alberta', update_params="false")
    process.start()
