import copy
import json
import logging
import math
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime
from logging.handlers import RotatingFileHandler
from urllib.parse import urlencode, urljoin

import scrapy


class BaseSpider(scrapy.Spider, ABC):
    allowed_domains = []

    def _set_crawler(self, crawler):
        super()._set_crawler(crawler)
        if self.settings.get('LOG_ENABLED', False):
            log_file_path = f"{self.settings.get('LOG_FILE_PATH')}" \
                            f"{self.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"

            logger = logging.getLogger()
            logger.setLevel(self.settings.get('LOG_LEVEL'))
            formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                                          '%Y-%m-%d %H:%M:%S')
            fhlr = RotatingFileHandler(log_file_path,
                                       maxBytes=50 * 1024 * 1024,
                                       backupCount=5,
                                       encoding='utf-8')
            fhlr.setLevel(self.settings.get('LOG_LEVEL'))
            fhlr.setFormatter(formatter)
            logger.addHandler(fhlr)


class LocationBaseSpider(BaseSpider):
    api_key = None
    locations = {'Alberta': 'lat=53.9332706&lng=-116.5765035',
                 'Ontario': 'lat=51.253775&lng=-85.323214'}
    base_url = None
    website_filter_id = None
    default_email = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stores = {}

    def parse_location(self, response):
        result = json.loads(response.text)
        if not result['success']:
            self.logger.warning(response.text)
            return

        for producer in result['results']['locations']:
            store_id = producer.get('id')
            buttons = producer.get('buttons')
            if buttons:
                url = buttons[0].get('pivot_button_value')
            else:
                url = f'{self.base_url}/pages/search-results-page?collection={producer["slug"]}'
            photos = producer.get('images')
            image_count = len(photos)
            item = {"Producer ID": "",
                    "p_id": store_id,
                    "Producer": producer.get('name'),
                    "Description": producer.get('description'),
                    "Link": url,
                    "SKU": "",
                    "City": producer.get('city'),
                    "Province": producer.get('state'),
                    "Store Name": producer.get('name'),
                    "Postal Code": producer.get('postcode'),
                    "long": producer.get('lng'),
                    "lat": producer.get('lat'),
                    "ccc": "",
                    "Page Url": url,
                    "Active": "",
                    "Main image": producer.get('cover_image'),
                    "Image 2": photos[0].get('high') if image_count > 0 else '',
                    "Image 3": photos[1].get('high') if image_count > 1 else '',
                    "Image 4": photos[2].get('high') if image_count > 2 else '',
                    "Image 5": photos[3].get('high') if image_count > 3 else '',
                    "Type": "",
                    "License Type": "",
                    "Date Licensed": "",
                    "Phone": producer.get('phone'),
                    "Phone 2": "",
                    "Contact Name": "",
                    "EmailPrivate": "",
                    "Email": producer.get('email') or self.default_email,
                    "Social": "",
                    "FullAddress": producer.get('display_address'),
                    "Address": producer.get('address'),
                    "Additional Info": "",
                    "Created": "",
                    "Comment": "",
                    "Updated": ""}
            yield item
            self.stores[store_id] = item

            yield scrapy.Request(url,
                                 callback=self.parse_store,
                                 meta={'store_id': store_id})

    def parse_store(self, response):
        if not self.api_key:
            indicator = 'script src="//www.searchanise.com/widgets/shopify/init.js?a='
            index1 = response.text.find(indicator)
            if index1 < 0:
                self.logger.warning(response.text)
                return
            index1 += len(indicator)
            index2 = response.text.find('">', index1)
            self.api_key = response.text[index1: index2]

        # Query products
        collection = response.xpath('//meta[@property="og:url"]/@content').extract_first()
        collection = collection.split('collection=')[-1]
        yield from self.query_collection(0, collection, response.meta.get('store_id'))

    def query_collection(self, current_page: int, collection: str, store_id: int):
        callback = ''.join(["{}".format(random.randint(0, 9)) for _ in range(0, 20)])
        callback = f'jQuery{callback}_{int(time.time() * 1000.0)}'
        params = {"api_key": self.api_key,
                  "q": "",
                  "sortBy": "title",
                  "sortOrder": "asc",
                  "restrictBy[quantity]": "1|",
                  "startIndex": str(current_page * 15),
                  "maxResults": "15",
                  "items": "true",
                  "pages": "true",
                  "categories": "true",
                  "suggestions": "true",
                  "queryCorrection": "true",
                  "suggestionsMaxResults": "3",
                  "pageStartIndex": "0",
                  "pagesMaxResults": "20",
                  "categoryStartIndex": "0",
                  "categoriesMaxResults": "20",
                  "facets": "true",
                  "facetsShowUnavailableOptions": "false",
                  "ResultsTitleStrings": "2",
                  "ResultsDescriptionStrings": "2",
                  "collection": collection,
                  "page": str(current_page + 1),
                  "displaySubcatProducts": "",
                  "prepareVariantOptions": "true",
                  "output": "jsonp",
                  "callback": callback,
                  "_": str(int(time.time() * 1000.0))}
        url = f'https://www.searchanise.com/getresults?{urlencode(params)}'
        yield scrapy.Request(url,
                             headers={'accept': '*/*'},
                             callback=self.parse_list,
                             meta={'page': current_page,
                                   'callback': callback,
                                   'collection': collection,
                                   'store_id': store_id})

    def parse_list(self, response):
        current_page = response.meta.get('page', 0)
        store_id = response.meta.get('store_id')
        store = self.stores[store_id]
        base_url = self.base_url
        if 'valuebuds.com' in base_url and (store['Province'] == 'Ontario' or store['Province'] == 'ON'):
            base_url = 'https://on.valuebuds.com/'

        data = response.text[len(response.meta['callback']) + 1: -2]
        data = json.loads(data)
        for one in data['items']:
            for variant in one['shopify_variants']:
                variant_url = urljoin(base_url, variant['link'])
                yield scrapy.Request(variant_url,
                                     callback=self.parse_details,
                                     meta={'store_id': store_id})

        if current_page == 0:
            total_pages = math.ceil(data['totalItems'] / data['itemsPerPage'])
            for index in range(1, total_pages):
                collection = copy.copy(response.meta['collection'])
                yield from self.query_collection(index, collection, store_id)

    @abstractmethod
    def parse_details(self, response):
        raise NotImplemented
